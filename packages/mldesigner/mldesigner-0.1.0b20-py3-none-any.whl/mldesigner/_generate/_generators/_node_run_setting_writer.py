# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from ast import literal_eval

from mldesigner._constants import ARM_ID_PREFIX
from mldesigner._generate._generators._base_generator import BaseGenerator
from mldesigner._utils import (
    _is_primitive_type,
    extract_input_output_name_from_binding,
    get_all_data_binding_expressions,
)

CONF_KEY_MAP = {
    "driver_cores": "spark.driver.cores",
    "driver_memory": "spark.driver.memory",
    "executor_cores": "spark.executor.cores",
    "executor_memory": "spark.executor.memory",
    "executor_instances": "spark.executor.instances",
    "dynamic_allocation_enabled": "spark.dynamicAllocation.enabled",
    "dynamic_allocation_min_executors": "spark.dynamicAllocation.minExecutors",
    "dynamic_allocation_max_executors": "spark.dynamicAllocation.maxExecutors",
}


def _dump_dict_to_str(data):
    input_params_list = []
    for k, v in data.items():
        if v:
            v = _process_data_of_binding_and_primitive(v)
            input_params_list.append(f"{k}={v}")
    return ", ".join(input_params_list)


def _process_data_of_binding_and_primitive(data):
    """
    We only support primitive type, dict, list, data bindings in run setting for now.
    """
    if get_all_data_binding_expressions(data, ["parent", "jobs"]):
        expression = get_all_data_binding_expressions(data, ["parent", "jobs"])
    elif get_all_data_binding_expressions(data, ["parent", "inputs"]):
        expression = get_all_data_binding_expressions(data, ["parent", "inputs"])
    elif get_all_data_binding_expressions(data, ["parent", "outputs"]):
        expression = get_all_data_binding_expressions(data, ["parent", "outputs"])
    elif _is_primitive_type(type(data)):
        return f"'{data}'" if isinstance(data, str) else data
    elif isinstance(data, (dict, list)):
        return data
    else:
        raise TypeError(f"{data} of type {type(data)} is not primitive value or binding string.")
    return extract_input_output_name_from_binding(expression[0])


class NodeRunSettingWriter:
    def __init__(self, node, logger):
        self.node = node
        self.logger = logger
        self.common_no_need_attribute_list = ["inputs", "outputs", "type"]
        self.run_setting = {}
        self.node_attribute_dict = self.node._to_dict()  # pylint: disable=protected-access
        self.sweep_objective = None
        self._delete_prefix_in_compute()

    def _delete_prefix_in_compute(self):
        if "compute" in self.node_attribute_dict.keys():
            match_result = re.match(f"{ARM_ID_PREFIX}(.*)", self.node_attribute_dict["compute"])
            if match_result and match_result.group(1):
                self.node_attribute_dict["compute"] = match_result.group(1)
            self.node_attribute_dict["compute"] = literal_eval(
                _process_data_of_binding_and_primitive(self.node_attribute_dict["compute"])
            )

    def conf_setter(self, attribute_value):
        conf_key_map = {v: k for k, v in CONF_KEY_MAP.items()}
        for attr, attr_value in attribute_value.items():
            try:
                renamed_attr = conf_key_map[attr]
                assert _is_primitive_type(type(attr_value))
                self.run_setting[renamed_attr] = f"'{attr_value}'" if isinstance(attr_value, str) else attr_value
            except KeyError:
                self.logger.warning(f"The conf attr: {attr} can't be used in Spark.conf initialize.")

    def _set_attribute(self, attribute, attribute_value, attr_setter_func):
        if attr_setter_func == "_set_limit_to":
            self._set_limit_to(attribute_value)
        elif attr_setter_func == "_set_attribute_to_one_line":
            self._set_attribute_to_one_line(attribute, attribute_value)
        elif attr_setter_func == "sweep_objective_dump_dict_to_str":
            self.sweep_objective = _dump_dict_to_str(attribute_value)
        elif attr_setter_func == "_dump_dict_to_str":
            self.run_setting[attribute] = _dump_dict_to_str(attribute_value)
        elif attr_setter_func == "directly_set":
            self.run_setting[attribute] = attribute_value
        elif attr_setter_func == "conf_set":
            self.conf_setter(attribute_value)
        else:
            raise AttributeError(f"attr_setter_func: {attr_setter_func} is not defined in NodeRunSettingWriter.")

    @property
    def attr_to_setter(self):
        return {
            "limits": "_set_limit_to",
            "early_termination": "_set_attribute_to_one_line",
            "resources": "_set_attribute_to_one_line",
            "retry_settings": "_set_attribute_to_one_line",
            "environment_variables": "_set_attribute_to_one_line",
            "identity": "_set_attribute_to_one_line",
            "distribution": "_set_attribute_to_one_line",
            "objective": "sweep_objective_dump_dict_to_str",
            "search_space": "directly_set",
            "partition_keys": "directly_set",
            "conf": "conf_set",
        }

    def _update_run_setting_dict(self):
        for attribute, attribute_value in self.node_attribute_dict.items():
            if attribute in self.common_no_need_attribute_list:
                continue
            if isinstance(attribute_value, str):
                self.run_setting[attribute] = f"'{attribute_value}'"
            elif _is_primitive_type(type(attribute_value)):  # attribute is int/float/bool
                self.run_setting[attribute] = attribute_value
            else:
                attr_setter_func = self.attr_to_setter[attribute]
                self._set_attribute(attribute, attribute_value, attr_setter_func)

    def _set_limit_to(self, attribute_value):
        if not attribute_value["timeout"]:
            return
        limit_str_list = []
        limit_attribute_list = ["timeout", "max_total_trials", "max_concurrent_trials", "trial_timeout"]
        for limit_attribute in limit_attribute_list:
            try:
                limit_attribute_value = attribute_value[limit_attribute]
                if limit_attribute_value:
                    limit_str_list.append(
                        f"{limit_attribute}=" f"{_process_data_of_binding_and_primitive(limit_attribute_value)}"
                    )
            except Exception:  # pylint: disable=broad-except
                continue
        limit_str = ", ".join(limit_str_list)
        limit_str = f"set_limits({limit_str})"
        self.run_setting[limit_str] = None

    def _set_attribute_to_one_line(self, attr, attribute_value):
        for k, v in attribute_value.items():
            if v:
                v = _process_data_of_binding_and_primitive(v)
                if attr not in self.run_setting.keys():
                    self.run_setting[attr] = {}
                self.run_setting[attr][k] = v
        # dump self.run_setting[attr] to str
        attr_dict = self.run_setting.pop(attr)
        generator = SingleDictGenerator(attr_dict)
        self.run_setting[attr] = generator.generate()

    def get(self, attribute, default_return_value):
        if hasattr(self, attribute):
            return getattr(self, attribute)
        return default_return_value


class CommandRunSettingWriter(NodeRunSettingWriter):
    def __init__(self, node, logger):
        super(CommandRunSettingWriter, self).__init__(node, logger)
        self.command_attribute_no_need = ["component", "command", "context", "old_base_path", "code", "services"]
        self.common_no_need_attribute_list.extend(self.command_attribute_no_need)
        self.command_attribute_need = [
            "limits",
            "environment",
            "compute",
            "environment_variables",
            "resources",
            "distribution",
            "identity",
            "comment",
        ]
        self._update_run_setting_dict()


class SparkRunSettingWriter(NodeRunSettingWriter):
    def __init__(self, node, logger):
        super(SparkRunSettingWriter, self).__init__(node, logger)
        self.spark_attribute_no_need = [
            "properties",
            "component",
            "args",
            "code",
            "jars",
            "files",
            "py_files",
            "archives",
            "entry",
        ]
        self.common_no_need_attribute_list.extend(self.spark_attribute_no_need)
        self.spark_attribute_need = ["conf", "environment", "comment", "compute", "resources", "identity"]
        self._update_run_setting_dict()


class ParallelRunSettingWriter(NodeRunSettingWriter):
    def __init__(self, node, logger):
        super(ParallelRunSettingWriter, self).__init__(node, logger)
        self.parallel_attribute_no_need = ["properties", "component", "schema_ignored", "task", "input_data"]
        self.common_no_need_attribute_list.extend(self.parallel_attribute_no_need)
        self.parallel_attribute_need = [
            "logging_level",
            "mini_batch_size",
            "partition_keys",
            "resources",
            "retry_settings",
            "max_concurrency_per_instance",
            "error_threshold",
            "mini_batch_error_threshold",
            "environment_variables",
            "comment",
            "compute",
        ]
        self._update_run_setting_dict()


class SweepRunSettingWriter(NodeRunSettingWriter):
    def __init__(self, node, logger):
        super(SweepRunSettingWriter, self).__init__(node, logger)
        self.sweep_attribute_no_need = ["properties", "trial"]
        self.common_no_need_attribute_list.extend(self.sweep_attribute_no_need)
        self.sweep_attribute_need = [
            "comment",
            "compute",
            "objective",
            "early_termination",
            "limits",
            "sampling_algorithm",
            "search_space",
        ]
        self._update_run_setting_dict()


class PipelineRunSettingWriter(NodeRunSettingWriter):
    pass


class SingleDictGenerator(BaseGenerator):
    def __init__(self, origin_dict):  # pylint: disable=unused-argument
        super(SingleDictGenerator, self).__init__()
        self.dict = origin_dict

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_line_break_dict.template"

    @property
    def entry_template_keys(self):
        return [
            "dict",
        ]
