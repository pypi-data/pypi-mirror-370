# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from mldesigner._azure_ai_ml import Input, Output
from mldesigner._exceptions import UserErrorException
from mldesigner._generate._generators._base_generator import BaseGenerator
from mldesigner._utils import _is_instance_of, _is_primitive_type

from ._node_run_setting_writer import (
    CommandRunSettingWriter,
    ParallelRunSettingWriter,
    PipelineRunSettingWriter,
    SparkRunSettingWriter,
    SweepRunSettingWriter,
    _dump_dict_to_str,
    _process_data_of_binding_and_primitive,
)


class SingleComponentFuncGenerator(BaseGenerator):
    def __init__(self, component_entity, component_func_name, logger, **kwargs):  # pylint: disable=unused-argument
        super(SingleComponentFuncGenerator, self).__init__()
        self._node = component_entity
        self.logger = logger
        self._node_name = self._node.name
        self._component_func_name = component_func_name
        self._params = self._get_params()
        node_runsetting_writer_dict = {
            "command": CommandRunSettingWriter,
            "spark": SparkRunSettingWriter,
            "parallel": ParallelRunSettingWriter,
            "sweep": SweepRunSettingWriter,
            "pipeline": PipelineRunSettingWriter,
        }
        self.node_runsetting_writer = node_runsetting_writer_dict[self._node.type](node=self._node, logger=self.logger)
        self.run_setting = self.node_runsetting_writer.run_setting
        self.sweep_objective = self.node_runsetting_writer.get("sweep_objective", None)

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_components_code_def.template"

    @property
    def entry_template_keys(self):
        return [
            "node_name",
            "component_func_name",
            "params",
            "run_setting",
            "sweep_objective",
        ]

    @property
    def node_name(self):
        return self._node_name

    @property
    def component_func_name(self):
        return self._component_func_name

    @property
    def params(self):
        return self._params

    @staticmethod
    def _get_input_name(data):
        """
        data may in the following types:
        1. Input: In this case, it needs to return an Input entity
        2. Output: In this case, the binding expression is stored in Output.path
        3. str: data can be an int/float in string format, like "1", "2.0",
            or a binding expression, like "${{parent.jobs.a_job.outputs.a_port}}", "${{parent.inputs.a_input}}"
        """
        if not data:
            return None
        if isinstance(data, Input):
            input_str = _dump_dict_to_str(data._to_dict())  # pylint: disable=protected-access
            return f"Input({input_str})"
        if isinstance(data, Output):
            data = data.path

        # data should be string through the above steps, otherwise raise error
        if not _is_primitive_type(type(data)):
            raise UserErrorException(f"Invalid data: {data}. The supported type here should be primitive.")

        return _process_data_of_binding_and_primitive(data)

    def _get_params(self):
        # pylint: disable=protected-access
        params_dict = {}
        for node_name, node_input in self._node.inputs.items():
            if isinstance(node_input, Input):
                params_dict[node_name] = self._get_input_name(data=node_input)
            elif _is_instance_of(node_input, "NodeInput"):
                if _is_primitive_type(type(node_input._data)) or isinstance(node_input._data, (Input, Output)):
                    params_dict[node_name] = self._get_input_name(data=node_input._data)
                elif isinstance(node_input._meta, Input):  # use meta to build an Input
                    params_dict[node_name] = self._get_input_name(data=node_input._meta)
                elif not node_input._meta and not node_input._data:
                    continue
                else:
                    raise UserErrorException(
                        f"""Supported input type/format is node_input._meta of Input,
                        node_input._data of (str, Input, Output).
                        Currently got node_input: {node_input}."""
                    )
            else:
                raise UserErrorException(f"Invalid data. The input type of node input is {type(node_input)}.")
        return params_dict
