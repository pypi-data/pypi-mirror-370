# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from pathlib import Path
from typing import Dict

from mldesigner._azure_ai_ml import Component, Pipeline, PipelineJob
from mldesigner._export._parse_url import _parse_designer_url
from mldesigner._generate._generators._base_generator import BaseGenerator
from mldesigner._generate._generators._module_generator import ModuleGenerator
from mldesigner._generate._generators._pipeline_generator import export_pkg_logger
from mldesigner._generate._generators.pipelines_folder_generator import PipelinesGenerator


def _rename_target_dir(target_dir):
    folder_id = 1
    renamed_target_dir = target_dir
    while Path(renamed_target_dir).exists():
        renamed_target_dir = str(Path(target_dir)) + f"_{folder_id}"
        folder_id += 1
    return Path(renamed_target_dir)


class AzuremlConfigGenerator(BaseGenerator):
    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        workspace_name: str,
    ):
        self.subscription_id = f'"{subscription_id}"'
        self.resource_group = f'"{resource_group}"'
        self.workspace_name = f'"{workspace_name}"'

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_azureml_config.template"

    @property
    def entry_template_keys(self) -> list:
        return [
            "subscription_id",
            "resource_group",
            "workspace_name",
        ]


class RunGenerator(BaseGenerator):
    def __init__(
        self,
        pipeline_job,
    ):
        self.pipeline_job = pipeline_job
        self.pipeline_folder_name = None

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_run.template"

    @property
    def entry_template_keys(self) -> list:
        return [
            "pipeline_job",
            "pipeline_folder_name",
        ]

    @property
    def pipeline_folder_name(self):
        return self._pipeline_folder_name

    @pipeline_folder_name.setter
    def pipeline_folder_name(self, folder_name):
        self._pipeline_folder_name = folder_name


class PipelineCodeGenerator:
    # TODO: create data folder
    # DATA_FOLDER_NAME = "data"

    def __init__(
        self,
        asset: str,
        pipeline_entity: PipelineJob,
        target_dir: Path,
        pattern_to_components: Dict[str, Component],
        pattern_to_pipeline_components: Dict[str, Component],
        pattern_to_subgraph_nodes: Dict[str, Pipeline],  # to provide inputs and outputs for PipelineComponent
        force_regenerate=False,
    ):
        self.target_dir = target_dir
        self._components = pattern_to_components
        self.component_generator = ModuleGenerator(
            assets=[asset],
            working_dir=Path("."),
            target_dir=Path("."),
            module_name="components",
            force_regenerate=force_regenerate,
            pattern_to_components={asset: list(self._components.values())},
        )
        self.pipelines_generator = PipelinesGenerator(
            pipeline_entity=pipeline_entity,
            pipeline_name="pipelines",
            force_regenerate=force_regenerate,
            pattern_to_components=self._components,
            pattern_to_pipeline_components=pattern_to_pipeline_components,
            pattern_to_subgraph_nodes=pattern_to_subgraph_nodes,
        )
        self._run_generator = RunGenerator(
            pipeline_job=pipeline_entity,
        )
        (
            subscription_id,
            resource_group,
            workspace_name,
            draft_id,  # pylint: disable=unused-variable
            run_id,  # pylint: disable=unused-variable
            endpoint_id,  # pylint: disable=unused-variable
            published_pipeline_id,  # pylint: disable=unused-variable
        ) = _parse_designer_url(pipeline_entity.studio_url)
        self._config_generator = AzuremlConfigGenerator(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace_name,
        )
        self._force_regenerate = force_regenerate

    def generate(self, target_dir: Path):
        if not self._components:
            return
        if target_dir.exists():
            target_dir = _rename_target_dir(target_dir)
            target_dir.mkdir(parents=True)
        self.component_generator.generate(target_dir=target_dir)
        self.pipelines_generator.generate(target_dir=target_dir)
        self._run_generator.pipeline_folder_name = target_dir
        self._run_generator.generate_to_file(target=target_dir / "run.py")
        azureml_config_dir = target_dir / ".azureml"
        azureml_config_dir.mkdir(parents=True)
        self._config_generator.generate_to_file(target=azureml_config_dir / "config.json")
        export_pkg_logger.info(msg=f"Pipeline export results were saved in {Path.absolute(target_dir)}")
