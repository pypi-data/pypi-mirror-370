# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
from pathlib import Path

from mldesigner._constants import ComponentSource, NodeType
from mldesigner._exceptions import MldesignerCompileError

from ._base_compiler import BaseCompiler
from ._component_compiler import CommandComponentCompiler, ParallelComponentCompiler


class PipelineComponentCompiler(BaseCompiler):
    """Pipeline component compiler to compile pipelines to yaml pipeline components"""

    PIPELINE_SCHEMA = "https://azuremlschemas.azureedge.net/latest/pipelineComponent.schema.json"

    def _update_compile_content(self):
        """Generate pipeline component dict and refine"""
        self._component_content = self._component._to_dict()
        self._component_content[BaseCompiler.SCHEMA_KEY] = self.PIPELINE_SCHEMA
        self._component_content["jobs"] = self._resolve_pipeline_jobs_dict()

    def _resolve_pipeline_jobs_dict(self) -> dict:
        jobs_dict = {}
        for node_name, node in self._component.jobs.items():
            jobs_dict[node_name] = self._resolve_pipeline_node_dict(
                node.component, self._component_content["jobs"][node_name]
            )
            # node level code is not needed for mldesigner compile result
            jobs_dict[node_name].pop("code", None)
            self._update_node_inputs(jobs_dict[node_name])
        return jobs_dict

    def _resolve_pipeline_node_dict(self, component, node_dict) -> dict:
        node_source = component._source

        # builder function as inline component in pipeline
        if node_source == ComponentSource.BUILDER:
            return self._resolve_builder_component_node(node_dict)
        if node_source == ComponentSource.MLDESIGNER:
            return self._resolve_mldesigner_component_node(component, node_dict)
        if node_source == ComponentSource.YAML_COMPONENT:
            return self._resolve_yaml_component_node(component, node_dict)
        if node_source == ComponentSource.DSL:
            return self._resolve_pipeline_component_node(component, node_dict)
        if node_source == ComponentSource.REMOTE_WORKSPACE_COMPONENT:
            return self._resolve_remote_workspace_component(node_dict)
        if node_source == ComponentSource.REMOTE_REGISTRY:
            return self._resolve_remote_registry_component(node_dict)

        msg = f"Component '{component.name}' failed: Unsupported node type '{node_source}'"
        raise MldesignerCompileError(message=msg)

    def _resolve_builder_component_node(self, node_dict) -> dict:
        self._update_component_inputs(node_dict["component"])
        return node_dict

    def _resolve_mldesigner_component_node(self, component, node_dict) -> dict:
        CommandComponentCompiler(component, self._collector).compile()
        if self._output:
            node_dict["component"] = f"../{component.name}/{component.name}.yaml"
            return node_dict

        start = Path(self._component._source_path)
        dest = Path(component._source_path)
        if start == dest:
            # indicates component and current pipeline are in the same source file
            relative_path = Path(f"./{component.name}.yaml")
        else:
            relative_path = Path(os.path.relpath(dest, start.parent)).parent / f"{component.name}.yaml"
        relative_path = relative_path.as_posix()
        node_dict["component"] = relative_path
        return node_dict

    def _resolve_yaml_component_node(self, component, node_dict) -> dict:
        if self._output:
            return self._resolve_yaml_component_node_with_output(component, node_dict)

        start = Path(self._component._source_path)
        dest = Path(component._source_path)
        relative_path = Path(os.path.relpath(dest, start.parent)).as_posix()
        node_dict["component"] = relative_path
        return node_dict

    def _resolve_yaml_component_node_with_output(self, component, node_dict) -> dict:
        """Resolve yaml component node dict when output folder is specified"""
        node_type = component.type
        if node_type == NodeType.COMMAND:
            CommandComponentCompiler(component, self._collector).compile()
        elif node_type == NodeType.PIPELINE:
            PipelineComponentCompiler(component, self._collector).compile()
        elif node_type == NodeType.PARALLEL:
            ParallelComponentCompiler(component, self._collector).compile()
        else:
            raise MldesignerCompileError(
                f"Unsupported node type '{node_type}' when compiling pipeline component '{self._component.name}'."
            )

        yaml_file_name = f"{component.name}.yaml"
        # if the component has original yaml, use original yaml file name
        if component._source == ComponentSource.YAML_COMPONENT:
            yaml_file_name = Path(component._source_path).name
        node_dict["component"] = f"../{component.name}/{yaml_file_name}"
        return node_dict

    @classmethod
    def _resolve_remote_workspace_component(cls, node_dict):
        name = node_dict["component"]["name"]
        version = node_dict["component"]["version"]
        # use component short format arm id
        node_dict["component"] = f"azureml:{name}:{version}"
        return node_dict

    @classmethod
    def _resolve_remote_registry_component(cls, node_dict):
        # use id which is registry component uri
        node_dict["component"] = node_dict["component"]["id"]
        return node_dict

    def _resolve_pipeline_component_node(self, component, node_dict) -> dict:
        PipelineComponentCompiler(component, self._collector).compile()
        if self._output:
            node_dict["component"] = f"../{component.name}/{component.name}.yaml"
            return node_dict

        relative_path = Path(os.path.relpath(component._source_path, self._component._source_path))
        if relative_path == Path("."):
            # indicates subgraph component and current pipeline are in the same source file
            relative_path = relative_path / Path(component._source_path).name
        relative_path = relative_path.parent / f"{component.name}.yaml"
        relative_path = relative_path.as_posix()
        node_dict["component"] = relative_path
        return node_dict

    @classmethod
    def _update_node_inputs(cls, node_dict):
        """Refine node inputs that has extra layer if it's a binding string"""
        node_inputs = node_dict["inputs"]
        for name, input_value in node_inputs.items():
            # original node inputs has extra layer if it's a binding string
            if isinstance(input_value, dict) and "path" in input_value:
                node_inputs[name] = input_value["path"]
