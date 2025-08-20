# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# cspell: ignore wsid, reusedrunid


def is_subgraph_node(run_info):
    """Check if a run is a subgraph node. It's child are subgraph nodes."""
    return run_info.get("runSource") == "SubGraphCloud"


def build_node_path_2_run_id(node_path_2_run_id, node_id_prefix, run_id, run_id_2_child_runs):
    child_runs = run_id_2_child_runs.get(run_id, [])
    for run_info in child_runs:
        child_run_id = run_info["name"]

        if not is_subgraph_node(run_info["properties"]):
            if node_id_prefix:
                prefix = f"{node_id_prefix}.{run_info['display_name']}"
            else:
                prefix = run_info["display_name"]
            node_path_2_run_id[prefix] = child_run_id
        else:
            prefix = node_id_prefix

        build_node_path_2_run_id(node_path_2_run_id, prefix, child_run_id, run_id_2_child_runs)


def _is_sub_node(node, prefix):
    node_path = node["node_path"][1]
    if "." not in node_path:
        return False
    parent, node = node_path.rsplit(".", 1)
    return parent == prefix


def is_subgraph_diff(node: dict):
    return node.get("is_subgraph")


def find_source_node_in_subgraph(node, output_name, node_path_2_children):
    selected_output_name = f"parent.{node['node_path'][1]}.{output_name}"

    for child in node_path_2_children[node["node_path"][1]]:
        for child_output_name, val in child["children"]:
            if val == selected_output_name:
                if is_subgraph_diff(child):
                    return find_source_node_in_subgraph(child, child_output_name, node_path_2_children)

                return child

    raise Exception("child not found: {} {}".format(node, selected_output_name))


def find_source_node(input_val, node_path_2_node, node_path_2_children):
    if input_val.startswith("parent."):
        # source from pipeline level input
        input_val = input_val[len("parent.") :]
        parent_node, name = input_val.rsplit(".", 1)
        parent_node = node_path_2_node[parent_node]
        val = None
        for port_name, node_path in parent_node["parents"]:
            if port_name == name:
                val = node_path
                break
        if not val:
            # optional input don't have parent
            return None
        return find_source_node(val, node_path_2_node=node_path_2_node, node_path_2_children=node_path_2_children)

    node_name, port_name = input_val.rsplit(".", 1)
    source_node = node_path_2_node[node_name]
    if is_subgraph_diff(source_node):
        # source is another subgraph's output
        return find_source_node_in_subgraph(source_node, port_name, node_path_2_children)
    # source is another step run's output
    return source_node


def filter_all_nodes(diff_nodes):
    """Return 1st non-reused nodes in diff nodes"""
    node_path_2_node = {n["node_path"][1]: n for n in diff_nodes}
    node_path_2_children = {}
    for node in diff_nodes:
        if is_subgraph_diff(node):
            sub_nodes = []
            for sub in diff_nodes:
                if _is_sub_node(sub, node["node_path"][1]):
                    sub_nodes.append(sub)
            node_path_2_children[node["node_path"][1]] = sub_nodes

    result = []
    for node in diff_nodes:
        if is_subgraph_diff(node):
            continue
        parents = []
        parent_reused = True
        for _, val in node.get("parents", []):
            parent_node = find_source_node(
                val, node_path_2_node=node_path_2_node, node_path_2_children=node_path_2_children
            )
            if parent_node:
                parents.append(parent_node)
                parent_reused = parent_reused and parent_node["is_reused"]

        # all parents reused but node not reused
        if parent_reused and not node["is_reused"]:
            result.append(node)
    return result


def add_reused_run_id_2_diff_nodes(diff_nodes, root_run_id, run_id_2_child_runs):
    node_path_2_run_id = {}
    build_node_path_2_run_id(node_path_2_run_id, None, root_run_id, run_id_2_child_runs)
    run_id_2_run_info = {}
    for _, child_nodes in run_id_2_child_runs.items():
        for child_node in child_nodes:
            run_id = child_node["name"]
            run_id_2_run_info[run_id] = child_node["properties"]
    for node in diff_nodes:
        node_path = node["node_path"][1]
        try:
            run_id = node_path_2_run_id[node_path]
            run_info = run_id_2_run_info[run_id]
            reused_run_id = run_info["azureml.reusedrunid"]
            node["reused_run_id"] = reused_run_id
        except KeyError:
            # ignore if failed to get run info
            pass


def find_1st_non_reused_nodes(diff_nodes, root_run_id, run_id_2_child_runs):
    """Iterate all nodes in the diff nodes and return the 1st non-reused nodes.

    :param diff_nodes: The diff nodes of the graph.
    :type diff_nodes: list
    :param root_run_id: The root run id of the graph.
    :type root_run_id: str
    :param run_id_2_child_runs: The run id to run info mapping.
    :type run_id_2_child_runs: dict
    """
    filtered_nodes = filter_all_nodes(diff_nodes)
    # add reused run id to the filtered nodes
    add_reused_run_id_2_diff_nodes(filtered_nodes, root_run_id, run_id_2_child_runs)
    return filtered_nodes
