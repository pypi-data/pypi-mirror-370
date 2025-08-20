# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


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


def is_subgraph(run_info):
    """Check if a run is a subgraph. It only has 1 child which is a subgraph node."""
    if run_info and run_info.get("StepType") == "SubGraphCloudStep":
        return True
    return False


def traverse_all_nodes(root_run_id, diff_nodes, run_id_2_child_runs):  # pylint: disable=too-many-statements
    """Traverse all nodes in the graph and generate the reuse report.

    :param root_run_id: The root run id of the graph.
    :type root_run_id: str
    :param diff_nodes: The diff nodes of the graph.
    :type diff_nodes: list
    :param run_id_2_child_runs: The run id to run info mapping.
    :type run_id_2_child_runs: dict
    """
    node_id_2_nodes = {}
    for node in diff_nodes:
        node_id = node["id"]
        if node_id not in node_id_2_nodes:
            node_id_2_nodes[node_id] = []
        node_id_2_nodes[node_id].append(node)

    node_path_2_run_id = {}
    build_node_path_2_run_id(node_path_2_run_id, None, root_run_id, run_id_2_child_runs)

    run_id_2_child_run_ids = {}
    run_id_2_run_info = {}
    for parent_run_id, child_nodes in run_id_2_child_runs.items():
        child_run_ids = []
        for child_node in child_nodes:
            run_id = child_node["name"]
            run_id_2_run_info[run_id] = child_node["properties"]
            child_run_ids.append(run_id)
        run_id_2_child_run_ids[parent_run_id] = child_run_ids

    run_id_2_node = {}
    for node in diff_nodes:
        run_id = node.get("run_id")
        if run_id:
            run_id_2_node[run_id[1]] = node
        else:
            node_path = node["node_path"][1]
            if node_path in node_path_2_run_id:
                run_id_2_node[node_path_2_run_id[node_path]] = node

    visited = {}
    filtered_nodes = []

    def find_run_id_from_node_id(parent_run_id, node_id):
        graph_node: dict = run_id_2_node.get(parent_run_id)
        node_prefix = graph_node["node_path"][1].rsplit(".", 1)[0]
        for node in node_id_2_nodes.get(node_id, []):
            child_node_prefix = node["node_path"][1].rsplit(".", 1)[0]
            if node_prefix == child_node_prefix:
                if "run_id" in node:
                    return node["run_id"][1]
                return node_path_2_run_id[node["node_path"][1]]
            if "." not in child_node_prefix and "." not in node_prefix:
                return node_path_2_run_id[node["node_path"][1]]
        raise Exception("node id not found: {} {}".format(parent_run_id, node_id))

    def visit_node(run_id):
        """Visit a node, return if traversal should terminate."""
        if run_id == "Not running":
            return False

        if run_id in visited:
            return visited[run_id]

        graph_node = run_id_2_node.get(run_id)

        # visit predecessors first
        result = False
        for parent_node_id in set(graph_node.get("parents", [])):
            parent_run_id = find_run_id_from_node_id(run_id, parent_node_id)
            result = visit_node(parent_run_id) or result
        if result:
            visited[run_id] = True
            return True

        # TODO: make this a parameter
        if graph_node.get("is_reused") is False:
            filtered_nodes.append(run_id)
            visited[run_id] = True
            return True

        run_info = run_id_2_run_info.get(run_id)
        if is_subgraph(run_info):
            sub_graph_run_id = run_id_2_child_run_ids[run_id][0]
            result = visit_subgraph(sub_graph_run_id)

            if result:
                visited[run_id] = True
                return True
        visited[run_id] = False
        return False

    def visit_subgraph(run_id):
        """Visit a subgraph, return if traversal should terminate."""
        children = run_id_2_child_run_ids[run_id]
        result = False
        for child_run_id in children:
            graph_node = run_id_2_node.get(child_run_id)
            if not graph_node:
                # control flow nodes don't have node info
                continue

            result = visit_node(child_run_id) or result

        return result

    run_id_2_node[root_run_id] = {"parents": None}
    visit_subgraph(root_run_id)

    first_non_reused_nodes = list(filter(lambda d: "run_id" in d and d["run_id"][1] in filtered_nodes, diff_nodes))

    return first_non_reused_nodes
