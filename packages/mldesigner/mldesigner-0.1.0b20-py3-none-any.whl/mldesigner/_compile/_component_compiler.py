# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from mldesigner._compile._base_compiler import BaseCompiler
from mldesigner._constants import ComponentSource
from mldesigner._utils import load_yaml


class CommandComponentCompiler(BaseCompiler):
    """Basic component compiler to compile command components to yaml components"""

    COMMAND_SCHEMA = "https://azuremlschemas.azureedge.net/latest/commandComponent.schema.json"

    def _update_compile_content(self):
        """Generate component dict and refine"""
        component_dict = self._component._to_dict()
        # code will always be the default value "." in compiled yaml
        self._snapshot = self._get_component_snapshot(component_dict.pop(self.CODE_KEY, None))
        self._refine_component_dict(component_dict)
        self._component_content = component_dict

    def _refine_component_dict(self, component_dict):
        """Update component dict for fields like schema, inputs and code"""
        # Add schema for command component
        component_dict[BaseCompiler.SCHEMA_KEY] = self.COMMAND_SCHEMA
        component_dict[self.CODE_KEY] = "."
        # transform dumped component input value to corresponding type
        self._update_component_inputs(component_dict)
        # pop name and version for environment
        self._refine_component_environment(component_dict)
        # additional_includes has already been added to snapshot_list in
        # self._get_component_snapshot => self._get_additional_includes, so remove it from component dict
        component_dict.pop("additional_includes", None)


class ParallelComponentCompiler(BaseCompiler):
    """Compiler to compile parallel components"""

    TASK_KEY = "task"
    PARALLEL_SCHEMA = "http://azureml/sdk-2-0/ParallelComponent.json"

    def _update_compile_content(self):
        """Generate component dict and refine"""
        component_dict = self._get_component_dict()
        code = component_dict[self.TASK_KEY].get(self.CODE_KEY, None)
        self._snapshot = self._get_component_snapshot(code)
        self._refine_component_dict(component_dict)
        self._component_content = component_dict

    def _get_component_dict(self):
        """Get component dict"""
        loaded_dict = self._component._to_dict()
        # for yaml component, load dict from yaml
        if self._component._source == ComponentSource.YAML_COMPONENT and self._component._source_path:
            yaml_dict = load_yaml(self._component._source_path)
            # in yaml dict, the environment may contain local env file path, need to update it with loaded_dict env
            yaml_dict[self.TASK_KEY]["environment"] = loaded_dict[self.TASK_KEY]["environment"]
            return yaml_dict
        # for other components, return loaded component dict
        return loaded_dict

    def _refine_component_dict(self, component_dict):
        """Update component dict for fields like schema, inputs and code"""
        # Add schema for command component
        component_dict[BaseCompiler.SCHEMA_KEY] = self.PARALLEL_SCHEMA
        component_dict[self.TASK_KEY][self.CODE_KEY] = "."
        # transform dumped component input value to corresponding type
        self._update_component_inputs(component_dict)
        # pop name and version for environment in task dict
        self._refine_component_environment(component_dict[self.TASK_KEY])


class SparkComponentCompiler(BaseCompiler):
    """Basic component compiler to compile spark components to yaml components"""

    SPARK_SCHEMA = "https://azuremlschemas.azureedge.net/latest/sparkComponent.schema.json"

    def _update_compile_content(self):
        """Generate component dict and refine"""
        component_dict = self._component._to_dict()
        # code will always be the default value "." in compiled yaml
        self._snapshot = self._get_component_snapshot(component_dict.pop(self.CODE_KEY, None))
        self._refine_component_dict(component_dict)
        self._component_content = component_dict

    def _refine_component_dict(self, component_dict):
        """Update component dict for fields like schema, inputs and code"""
        # Add schema for spark component
        component_dict[BaseCompiler.SCHEMA_KEY] = self.SPARK_SCHEMA
        component_dict[self.CODE_KEY] = "."
        # transform dumped component input value to corresponding type
        self._update_component_inputs(component_dict)
        # pop name and version for environment
        self._refine_component_environment(component_dict)
        # additional_includes has already been added to snapshot_list in
        # self._get_component_snapshot => self._get_additional_includes, so remove it from component dict
        component_dict.pop("additional_includes", None)
