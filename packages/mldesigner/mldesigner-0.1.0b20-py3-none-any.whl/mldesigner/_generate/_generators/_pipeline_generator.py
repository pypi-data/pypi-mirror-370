# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from typing import List, Union

from mldesigner._azure_ai_ml import Component, Input, Output, Pipeline, PipelineComponent, PipelineJob
from mldesigner._generate._generators._base_generator import BaseGenerator
from mldesigner._generate._generators._component_func_generator import SingleComponentFuncGenerator
from mldesigner._logger_factory import _LoggerFactory
from mldesigner._utils import (
    _get_node_io_name,
    extract_input_output_name_from_binding,
    get_all_data_binding_expressions,
)

export_pkg_logger = _LoggerFactory.get_logger("export")


class PipelineGenerator(BaseGenerator):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        pipeline_node: PipelineJob,
        pipeline_component: Union[PipelineJob, PipelineComponent],
        sorted_nodes: List[Component],
        sorted_nodes_func_name_list: List[str],
        pipeline_func_name: str,
    ):
        self.pipeline_node = pipeline_node
        self.pipeline_component = pipeline_component
        self._sorted_nodes = sorted_nodes
        self._component_func_names = sorted_nodes_func_name_list
        self.pipeline_func_name = pipeline_func_name
        self.url = None if isinstance(self.pipeline_component, PipelineComponent) else self.pipeline_node.studio_url
        self.logger = export_pkg_logger

        self.component_import, self.sub_pipeline_import = self.sub_pipeline_and_component_import()
        self._node_generators = [
            SingleComponentFuncGenerator(self._sorted_nodes[i], self._component_func_names[i], self.logger)
            for i in range(len(self._sorted_nodes))
        ]
        self.contain_float_or_number = False
        self.pipeline_param_defines, self.pipeline_param_assignments = self._pipeline_param_traversal()

    def sub_pipeline_and_component_import(self):
        sub_pipeline_import = {}
        component_import = []
        _node_id_to_func_name_dict = {
            node._instance_id: func_name  # pylint: disable=protected-access
            for node, func_name in zip(self._sorted_nodes, self._component_func_names)
        }
        for node in self._sorted_nodes:
            node_id = node._instance_id  # pylint: disable=protected-access
            if isinstance(node, Pipeline):
                sub_pipeline_import[_node_id_to_func_name_dict[node_id]] = _node_id_to_func_name_dict[node_id]
                if node.name == _node_id_to_func_name_dict[node_id]:
                    sub_pipeline_import[_node_id_to_func_name_dict[node_id]] += (
                        " as " + _node_id_to_func_name_dict[node_id] + "_func"
                    )
                    _node_id_to_func_name_dict[node_id] += "_func"
            else:
                component_import.append(_node_id_to_func_name_dict[node_id])
                if node.name == _node_id_to_func_name_dict[node_id]:
                    _node_id_to_func_name_dict[node_id] += "_func"
                    component_import[-1] += " as " + _node_id_to_func_name_dict[node_id]

        component_list_n = list(set(component_import))
        component_list_n.sort(key=component_import.index)
        # use _node_id_to_func_name_dict.values() to update self._component_func_names
        self._component_func_names = list(_node_id_to_func_name_dict.values())
        return component_list_n, sub_pipeline_import

    @property
    def run_setting(self):
        run_setting_dict = {}
        if hasattr(self.pipeline_node, "settings"):
            settings_dict = self.pipeline_node.settings._to_dict()  # pylint: disable=protected-access
            for setting_key, setting_value in settings_dict.items():
                if setting_value and not setting_key.startswith("_"):
                    run_setting_dict[f"settings.{setting_key}"] = setting_value
        if hasattr(self.pipeline_node, "compute"):
            run_setting_dict["settings.default_compute"] = getattr(self.pipeline_node, "compute")
        if self.pipeline_node.properties.get("azureml.defaultDataStoreName", None):
            run_setting_dict["settings.default_datastore"] = self.pipeline_node.properties[
                "azureml.defaultDataStoreName"
            ]
        return run_setting_dict

    @property
    def azure_ai_ml_imports(self):
        return [
            "from azure.ai.ml import Input, dsl",
        ]

    @property
    def dsl_pipeline_param_assignments(self):
        dsl_pipeline_param_dict = {}
        if self.pipeline_node.display_name:
            dsl_pipeline_param_dict["display_name"] = f'"{self.pipeline_node.display_name}"'
        if self.pipeline_node.description:
            dsl_pipeline_param_dict["description"] = f'"{self.pipeline_node.description}"'
        return dsl_pipeline_param_dict

    def _pipeline_param_traversal(self):
        pipeline_param_def_dict, pipeline_param_assign_dict, pipeline_param_def_with_default_dict = {}, {}, {}
        for pipeline_name, pipeline_input in self.pipeline_component.inputs.items():
            # pylint: disable=protected-access
            input_name = (
                _get_node_io_name(pipeline_input)
                if hasattr(pipeline_input, "_port_name") or hasattr(pipeline_input, "_name")
                else pipeline_name
            )
            input_value = pipeline_input._data if hasattr(pipeline_input, "_data") else pipeline_input
            if get_all_data_binding_expressions(input_value, ["parent", "inputs"]):
                # current pipeline must be a subgraph
                # hard-code to None because the input_value won't be used in subgraph initialization
                pipeline_param_def_with_default_dict[f"{input_name}: Input(type='{pipeline_input._type}')"] = None
                pipeline_param_assign_dict[input_name] = None
            elif isinstance(input_value, str):
                # input_value is an int/float/bool in the format of string or other strings
                if re.compile(r"^(-?[0-9]\d*)(\.\d+|\d*)$").match(input_value):
                    self.contain_float_or_number = True
                pipeline_param_def_with_default_dict[input_name] = f'"{input_value}"'
                pipeline_param_assign_dict[input_name] = f'"{input_value}"'
            elif isinstance(input_value, Input):  # input_value is an Input
                pipeline_param_def_dict[f"{input_name}: Input(type='{input_value.type}')"] = None
                input_params_list = []
                for k, v in input_value.items():
                    if v:
                        input_params_list.append(f'{k}="{v}"')
                input_str = ", ".join(input_params_list)
                pipeline_param_assign_dict[input_name] = f"Input({input_str})"
            else:
                raise TypeError(
                    f"""We don't support input_value of type {type(input_value)}.
                    The supported types include data_binding, primitive and Input."""
                )
        # let non-default param be the first keys of pipeline_param_def_dict
        pipeline_param_def_dict.update(pipeline_param_def_with_default_dict)
        return pipeline_param_def_dict, pipeline_param_assign_dict

    @property
    def pipeline_outputs(self):
        pipeline_output_dict = {}
        for node in self.pipeline_component.jobs.values():
            node_name = node.name
            for output in node.outputs.values():
                # pylint: disable=protected-access
                node_output_name = _get_node_io_name(output)
                pipeline_output_name = self._get_pipeline_output_name(output._data)
                if pipeline_output_name:
                    pipeline_output_dict[pipeline_output_name] = f"{node_name}.outputs.{node_output_name}"
        return pipeline_output_dict

    @classmethod
    def _get_pipeline_output_name(cls, name):
        if isinstance(name, Output):
            name = name.path
        expression = get_all_data_binding_expressions(name, ["parent", "outputs"])
        if expression:
            return extract_input_output_name_from_binding(expression[0])

    @property
    def component_node_strs(self):
        return [g.generate() for g in self._node_generators]

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_pipeline_def.template"

    @property
    def entry_template_keys(self) -> list:
        return [
            "url",
            "contain_float_or_number",
            "azure_ai_ml_imports",
            "component_import",
            "sub_pipeline_import",
            "dsl_pipeline_param_assignments",
            "pipeline_param_defines",
            "pipeline_func_name",
            "component_node_strs",
            "pipeline_outputs",
            "pipeline_param_assignments",
            "pipeline_node",
            "run_setting",
        ]
