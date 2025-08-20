# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Dict, List

from mldesigner._azure_ai_ml import Component, Pipeline, PipelineComponent, PipelineJob, Sweep
from mldesigner._export._cycle_validator import CycleValidator
from mldesigner._generate._generators._module_generator import (
    _get_selected_component_name,
    get_unique_component_func_name,
)
from mldesigner._generate._generators._pipeline_generator import PipelineGenerator, export_pkg_logger


def _pipeline_get_unique_component_func_names(components: List[Component]):
    """Try to return unique component func names, raise exception when duplicate component are found."""
    func_name_to_component = []
    name_version_to_func_name = {}

    for component in components:
        component_selected_name = _get_selected_component_name(component)
        name_version = f"{component_selected_name}:{component.version}"

        # use name_version to judge whether two components are same
        if name_version in name_version_to_func_name:
            func_name = name_version_to_func_name[name_version]
            func_name_to_component.append(func_name)
            continue

        name_candidate = get_unique_component_func_name(func_name_to_component, component)
        func_name_to_component.append(name_candidate)
        name_version_to_func_name[name_version] = name_candidate
    return func_name_to_component


class PipelinesGenerator:
    PIPELINE_INIT_NAME = "__init__.py"
    PIPELINE_SUBGRAPHS_NAME = "subgraphs"

    def __init__(
        self,
        pipeline_entity: PipelineJob,
        pipeline_name: str,
        pattern_to_components: Dict[str, Component],
        pattern_to_pipeline_components: Dict[str, PipelineComponent],
        pattern_to_subgraph_nodes: Dict[str, Pipeline],
        force_regenerate=False,
    ):
        self._name_to_component = pattern_to_components
        self._pipeline_name = pipeline_name
        self.pipeline_entity = pipeline_entity
        self.pattern_to_pipeline_components = pattern_to_pipeline_components
        self.pattern_to_subgraph_nodes = pattern_to_subgraph_nodes
        self.name_version_to_func_name = self._get_name_version_to_func_name()

        self._sub_pipeline_generators = [
            self._get_sorted_node_and_func_names(
                self.name_version_to_func_name[node.component],
                node,
                self.pattern_to_pipeline_components[node.component],
            )
            for node in self.pattern_to_subgraph_nodes.values()
        ]

        self._pipeline_generator = self._get_sorted_node_and_func_names(
            pipeline_entity.display_name, pipeline_entity, pipeline_entity
        )

        self._force_regenerate = force_regenerate

    def _get_name_version_to_func_name(self):
        # consistent with the sequence of ModuleGenerator
        sorted_name_to_component_list = sorted(self._name_to_component.items(), key=lambda x: x[0])
        name_version_list = [item[0] for item in sorted_name_to_component_list]
        name_version_list.extend(self.pattern_to_pipeline_components.keys())

        # put component at first, thus the name of component would be same with which generated in ModuleGenerator
        component_list = [item[1] for item in sorted_name_to_component_list]
        component_list.extend(self.pattern_to_pipeline_components.values())
        all_func_names = _pipeline_get_unique_component_func_names(component_list)

        return dict(zip(name_version_list, all_func_names))

    def _get_sorted_node_and_func_names(self, func_name, graph, graph_component):
        jobs = []
        for k, v in graph_component.jobs.items():
            if not v.name:
                v.name = k
            jobs.append(v)
        _sorted_nodes = CycleValidator.sort(jobs)
        # get component func name according to node.component
        sorted_nodes_func_name_list = []
        for node in _sorted_nodes:
            component_str = node.trial if isinstance(node, Sweep) else node.component
            sorted_nodes_func_name_list.append(self.name_version_to_func_name[component_str])
        return PipelineGenerator(
            pipeline_node=graph,
            pipeline_component=graph_component,
            sorted_nodes=_sorted_nodes,
            sorted_nodes_func_name_list=sorted_nodes_func_name_list,
            pipeline_func_name=func_name,
        )

    def generate(self, target_dir: Path):
        if not self._name_to_component:
            return
        target_pipeline_folder = target_dir / self._pipeline_name
        subgraph_folder = target_pipeline_folder / self.PIPELINE_SUBGRAPHS_NAME

        self.generate_folder(target_pipeline_folder, "pipeline")
        self.generate_folder(subgraph_folder, "subgraph")

        self._pipeline_generator.generate_to_file(target_pipeline_folder / f"{os.path.basename(target_dir)}.py")
        for _sub_pipeline_generator in self._sub_pipeline_generators:
            name = _sub_pipeline_generator.pipeline_func_name
            _sub_pipeline_generator.generate_to_file(subgraph_folder / f"{name}.py")

        with open(target_pipeline_folder / self.PIPELINE_INIT_NAME, "w") as f:
            f.close()

    def generate_folder(self, folder_name, pipeline_type):
        if folder_name.exists():
            if not self._force_regenerate:
                msg = f"Skip generating {pipeline_type} {folder_name.as_posix()} since it's already exists."
                export_pkg_logger.warning(msg)
                return
        else:
            folder_name.mkdir(parents=True)
