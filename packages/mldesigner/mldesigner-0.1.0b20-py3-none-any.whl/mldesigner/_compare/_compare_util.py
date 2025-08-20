# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module,import-error, too-many-nested-blocks, too-many-boolean-expressions
import copy
import json
import re
from typing import Dict, List, Union

from azure.ml.component._restclients.designer.models import (
    GraphModuleNode,
    GraphModuleNodeRunSetting,
    GraphReferenceNode,
)

PRIMITIVE_TYPE = (int, str, float, bool, bytes)


def _convert_to_json(content):
    try:
        content = json.loads(content)
        # ignore component id in ComponentIdentifier
        if content and "ComponentConfiguration" in content:
            if content["ComponentConfiguration"] and "ComponentIdentifier" in content["ComponentConfiguration"]:
                component_config = content["ComponentConfiguration"]["ComponentIdentifier"]
                component_id = re.findall("components/id/([^/&?}]+$)", component_config)
                if component_id:
                    content["ComponentConfiguration"]["ComponentIdentifier"] = re.sub(
                        component_id[0], "***", component_config
                    )
    except Exception:  # pylint: disable=broad-except
        # ignore component id in ComponentIdentifier
        if isinstance(content, str):
            component_id = re.findall('components/id/([^/&?}\n"]+)', content)
            if component_id:
                content["ComponentConfiguration"]["ComponentIdentifier"] = re.sub(component_id[0], "***", content)
        return content
    return content


def _convert_v2_parameter_name(node: Union[dict, list]):
    """
    Since v2 keep original group name for parameter name，but v1.5 will update "." to "_". We will convert v2
    parameter name to be consistent with the style of v1.5.
    """
    if isinstance(node, dict):
        if "value_type" in node and node["value_type"] == "GraphParameterName":
            if "value" in node and isinstance(node["value"], str):
                node["value"] = node["value"].replace(".", "_")
        for key, value in node.items():
            node[key] = _convert_v2_parameter_name(value)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            if isinstance(item, PRIMITIVE_TYPE):
                continue
            node[index] = _convert_v2_parameter_name(item)
    return node


def _remove_unconnected_input_settings(node: GraphReferenceNode, node_id2input_port_name: dict):
    """Remove unconnected input settings.

    :param node: Graph reference node
    :type: GraphReferenceNode
    :param node_id2input_port_name: Node id to input port name mapping
    :type : dict
    """
    remove_index = []
    for index, input_setting in enumerate(node.module_input_settings):
        if node.id in node_id2input_port_name and input_setting.name in node_id2input_port_name[node.id]:
            continue
        remove_index.append(index)
    remove_index = sorted(remove_index, reverse=True)

    for index in remove_index:
        node.module_input_settings.pop(index)


def _update_module_parameter(node: GraphModuleNode):
    """
    1. For Concatenate value type, will extract elements in assignmentsToConcatenate to make v2 and v1.5 comparable
    2. Since v2 will remove empty parameter in module_parameters of GraphModuleNode, but v1.5 will keep them. We will
    remove empty parameter name to simplify the compare result.
    3. Remove 'MLCComputeType' module parameter since the MLCCompute type of 1.5 is passed from the client, and there
    is no setting value when the pipeline component is registered. But MT call api resolved value according to the
    compute in v2, so there's value
    4. If node.use_graph_default_compute is True, we also will
    remove all compute relevant parameter, hack here as "Target" and "MLCComputeType".

    :param node: Graph module node
    :type: GraphModuleNode
    """
    # For Concatenate value type, will extract elements in assignmentsToConcatenate to make v2 and v1.5 comparable
    remove_index = []
    extracted_elements = []
    for index, module_parameter in enumerate(node.module_parameters):
        if module_parameter.value_type == "Concatenate":
            if module_parameter.assignments_to_concatenate:
                remove_index.append(index)
                for item in module_parameter.assignments_to_concatenate:
                    item.name = item.name if item.name else module_parameter.name
                    extracted_elements.append(item)

    remove_index = sorted(remove_index, reverse=True)
    for index in remove_index:
        node.module_parameters.pop(index)
    node.module_parameters.extend(extracted_elements)

    remove_index = []
    for index, module_parameter in enumerate(node.module_parameters):
        if (
            (hasattr(module_parameter, "value") and module_parameter.value is None)
            or (hasattr(module_parameter, "name") and module_parameter.name == "MLCComputeType")
            or (
                node.use_graph_default_compute
                and hasattr(module_parameter, "name")
                and (module_parameter.name == "MLCComputeType" or module_parameter.name == "Target")
            )
        ):
            remove_index.append(index)

    remove_index = sorted(remove_index, reverse=True)
    for index in remove_index:
        node.module_parameters.pop(index)
    return node


def _update_node_run_setting(node_run_setting: GraphModuleNodeRunSetting):
    """
    1. If use_graph_default_compute is True, we will skip compare this runsetting.
    2. Remove mlc_compute_type field since the MLCCompute type of 1.5 is passed from the client, and there is no setting
    value when the pipeline component is registered. But MT call api resolved value according to the compute in v2, so
    there's value

    :param node_run_setting: Graph module node runsetting
    :type: GraphModuleNodeRunSetting
    """
    remove_index = []
    for index, module_parameter in enumerate(node_run_setting.run_settings):
        if hasattr(module_parameter, "mlc_compute_type"):
            module_parameter.mlc_compute_type = None
        if hasattr(module_parameter, "use_graph_default_compute") and module_parameter.use_graph_default_compute:
            remove_index.append(index)

    remove_index = sorted(remove_index, reverse=True)
    for index in remove_index:
        node_run_setting.run_settings.pop(index)
    return node_run_setting


def write_data_to_json_file(data, json_file_name):
    with open(json_file_name, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=4)


def _get_output_name_2_output_setting_mapping(output_settings: List):
    """
    Get a mapping from output name to output setting.

    :param output_setting
    :type: list
    """

    output_name_2_output_setting_mapping = {}
    for output_setting in output_settings:
        output_name_2_output_setting_mapping[output_setting.name] = output_setting
    return output_name_2_output_setting_mapping


def _get_binding_output_name_mapping(edges: list):
    """
    Get a mapping from (node output name, node id) to pipeline output name if it's a binding case.

    :param edges: Edge information in current graph layer
    :type: list
    """
    binding_output_name_mapping = {}

    for edge in edges:
        if edge.destination_input_port.graph_port_name and edge.destination_input_port.node_id is None:
            node_id = edge.source_output_port.node_id
            node_output_name = edge.source_output_port.port_name
            binding_output_name_mapping[(node_id, node_output_name)] = edge.destination_input_port.graph_port_name
    return binding_output_name_mapping


def _update_node_output_setting(
    node: Union[GraphModuleNode, GraphReferenceNode],
    binding_output_name_mapping,
    pipeline_output_settings,
    node_data_path_parameters_mapping,
    root_pipeline_default_datastore,
):
    """
    Update node output setting.

    :param node
    :type: Union[GraphModuleNode, GraphReferenceNode]
    :param binding_output_name_mapping1
    :type: dict
    :param pipeline_output_settings
    :type: dict
    :param node_data_path_parameters_mapping
    :type: dict
    :param root_pipeline_default_datastore
    :type: str
    """
    for index, module_output_setting in enumerate(node.module_output_settings):
        if (
            pipeline_output_settings
            and binding_output_name_mapping
            and (node.id, module_output_setting.name) in binding_output_name_mapping
        ):
            pipeline_output_name = binding_output_name_mapping[(node.id, module_output_setting.name)]
            node.module_output_settings[index] = copy.deepcopy(pipeline_output_settings[pipeline_output_name])
            node.module_output_settings[index].name = module_output_setting.name
            node.module_output_settings[index].data_reference_name = module_output_setting.data_reference_name
        else:
            # If the output has no binding and other additional configurations, and there is a known issue on the MT
            # side. Before the pipeline runs, the graph returned by the call graphNoStatus API is not exactly the same
            # as the actual running graph (currently found that it may be data_store_name, and the compute), we will
            # update node datastore name to root pipeline default datastore name to deal with this situation specially.
            if node.use_graph_default_datastore or (
                isinstance(node.module_output_settings[index].data_store_name, str)
                and bool(re.search(r"^\$\{\{(.*?)\}\}$", node.module_output_settings[index].data_store_name))
            ):
                node.module_output_settings[index].data_store_name = root_pipeline_default_datastore
        # In root pipeline, pipeline output data_store_name may be None and we can get data_store_name from
        # graph.entity_interface.data_path_parameters if have
        if (
            node.module_output_settings[index].data_store_name is None
            and node_data_path_parameters_mapping
            and node.module_output_settings[index].parameter_name in node_data_path_parameters_mapping
        ):
            if node_data_path_parameters_mapping[node.module_output_settings[index].parameter_name].default_value:
                data_store_name = node_data_path_parameters_mapping[
                    node.module_output_settings[index].parameter_name
                ].default_value.data_store_name
            else:
                data_store_name = None
            if data_store_name and data_store_name != "None":
                node.module_output_settings[index].data_store_name = data_store_name
        # In root pipeline, we will prior data_store_mode in entity_interface if have instead of mode in pipeline
        # output setting.
        if (
            node_data_path_parameters_mapping
            and node.module_output_settings[index].parameter_name in node_data_path_parameters_mapping
        ):
            if node_data_path_parameters_mapping[node.module_output_settings[index].parameter_name].default_value:
                data_store_mode = node_data_path_parameters_mapping[
                    node.module_output_settings[index].parameter_name
                ].default_value.data_store_mode
            else:
                data_store_mode = None

            # add flag to judge whether it's from pipeline root entity interface mode
            if data_store_mode:
                node.module_output_settings[index].data_store_mode = "_".join((data_store_mode, "from_pipeline"))
    # Since path_on_datastore will have an extra escape ending in v2 which won't affect reuse. We will strip escape
    # ending in node.module_output_settings.dataset_output_options.path_on_datastore in v2 to be consistent with v1.5.
    for module_output_setting in node.module_output_settings:
        if (
            module_output_setting
            and module_output_setting.dataset_output_options
            and module_output_setting.dataset_output_options.path_on_datastore
        ):
            path = module_output_setting.dataset_output_options.path_on_datastore
            if isinstance(path, str):
                module_output_setting.dataset_output_options.path_on_datastore = path.rstrip("/")

    for module_output_setting in node.module_output_settings:
        module_output_setting.data_store_name_parameter_assignment = concatenate_output_value(
            module_output_setting.data_store_name_parameter_assignment
        )
        module_output_setting.dataset_output_options.path_on_datastore_parameter_assignment = \
            concatenate_output_value(
                module_output_setting.dataset_output_options.path_on_datastore_parameter_assignment
            )
    return node.module_output_settings


def concatenate_output_value(node_output):
    # We will change value type to Concatenate and set name to None to make v2 and v1.5 comparable, v1.5 won't have
    # name field.
    if node_output:
        if node_output.assignments_to_concatenate is None:
            node_output.assignments_to_concatenate = [copy.deepcopy(node_output)]
            node_output.value_type = "Concatenate"
            node_output.value = None
            node_output.name = None
        else:
            node_output.name = None
    return node_output


def _get_data_path_parameters_mapping(node_graph_detail):
    """
    Get data_path_parameters and save as a mapping from name to data_path_parameters

    :param node_graph_detail
    :type: GraphUtil
    """

    data_path_parameters_mapping = {}
    if (
        node_graph_detail.graph
        and node_graph_detail.graph.entity_interface
        and node_graph_detail.graph.entity_interface.data_path_parameters
    ):
        data_path_parameters = node_graph_detail.graph.entity_interface.data_path_parameters
        for data_path_parameter in data_path_parameters:
            data_path_parameters_mapping[data_path_parameter.name] = data_path_parameter
    return data_path_parameters_mapping


# pylint: disable=no-else-return, too-many-return-statements
def _validate_not_empty_data(data: Union[Dict, List, int, str, float, bool, bytes]):
    """
    validate whether data is empty or not
    """

    if data is None:
        return False
    if isinstance(data, dict):
        if len(data) == 0:
            return False
        for _, value in data.items():
            result = _validate_not_empty_data(value)
            if result:
                return True
        return False
    elif isinstance(data, list):
        if len(data) == 0:
            return False
        for value in data:
            result = _validate_not_empty_data(value)
            if result:
                return True
        return False
    elif isinstance(data, str):
        if not data:
            return False
        return True
    else:
        return True
