# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
class _ModuleNode(object):
    """Used to save graph module nodes info for cycle tracking."""

    def __init__(self, node_id, node_entity):
        self.node_id = node_id
        self.node_entity = node_entity
        self.outputs = []
        self.inputs = []


class _NodeStatus(object):
    """When checking for cycles in the graph, keep track of which nodes have been visited."""

    # Initial state (not visited yet)
    NOT_VISITED = 0
    # Visited in current path
    VISITED_IN_CUR_PATH = 1
    # Visited in other path
    VISITED_IN_OTHER_PATH = 2


class CycleValidator:
    """This class is used for checking module-cycles in pipeline"""

    @staticmethod
    def sort(pipeline_steps):
        """Topological sort graph nodes."""
        graph_nodes = CycleValidator._construct_graph_from_dto(pipeline_steps)
        _, sorted_nodes = CycleValidator._validate_cycles(pipeline_steps, graph_nodes)
        sorted_nodes = [node.node_entity for node in sorted_nodes]
        return sorted_nodes

    @staticmethod
    def _validate_cycles(pipeline_steps, graph_nodes):
        """
        Check for cycle in the graph.

        :param pipeline_steps: got from VisualizationContext.step_nodes
        :type pipeline_steps: List[Command]
        :return: cycle_detected: detected cycle, empty if no cycle is detected
        :rtype: list
        """
        # Detect all cycles
        cycle_detected, sorted_nodes = CycleValidator._detect_cycles(graph_nodes)
        # Handle exception
        if cycle_detected:
            cycles_nodes = []
            for node in cycle_detected:
                step = next(item for item in pipeline_steps if item.id == node.node_id)
                # use component name in error message when available
                step_id = step.component_name if getattr(step, "component_name", None) else step.id
                cycles_nodes.append("{0}({1})".format(step.name, step_id))
        return cycle_detected, sorted_nodes

    @staticmethod
    def _get_prior_port_name(port_name):
        from mldesigner._utils import get_all_data_binding_expressions
        from mldesigner._azure_ai_ml import Output

        if isinstance(port_name, Output):
            port_name = port_name.path
        expression = get_all_data_binding_expressions(port_name, ["parent", "jobs"])
        if expression:
            return expression[0].split(".")[2]
        return None

    @staticmethod
    def _construct_graph_from_dto(job_entity_jobs):
        job_ModuleNode = {job.name: _ModuleNode(job.name, job) for job in job_entity_jobs}
        for job in job_entity_jobs:
            for job_input in job.inputs.values():
                # pylint: disable=protected-access
                prior_port_name = CycleValidator._get_prior_port_name(job_input._data)
                if prior_port_name:
                    job_ModuleNode[job.name].inputs.append(job_ModuleNode[prior_port_name])
                    job_ModuleNode[prior_port_name].outputs.append(job_ModuleNode[job.name])
        return list(job_ModuleNode.values())

    @staticmethod
    def _detect_cycles(graph_nodes):
        """
        Detect cycles in pipeline. Iterate nodes in graph, do a dfs for each node, return cycle once cycle is detected.

        Prove:
        1. algorithm is not infinite: iterate over finite number graph nodes, for each iteration, only push not_visited
           node into stack, stack pops, one iteration will stop when stack became empty.
        2. if return cycle_detected is not empty, nodes inside are cycle nodes. when the algo encountered starting node
           again, a cycle must be detected. Besides, we use this_cyc with hierarchical level to maintain a path from
           starting node to current node, therefore, returned nodes in cycle_detected is the cycle vertexes.
        3. if there exit a cycle in the graph, this algo can detect it. Because this algo will do a dfs for each node,
           it will start search from one vertex node in that cycle for sure, by then, that cycle will be detected.

        :param graph_nodes: module nodes in pipeline
        :rtype graph_nodes: list
        :return cycle_detected: cycle detected, empty if no cycle is detected
        :rtype cycle_detected: list
        """
        cycle_detected = []
        node_status = {}
        ordered_nodes = []
        for module_node in graph_nodes:
            node_status[module_node.node_id] = _NodeStatus.NOT_VISITED

        for node in graph_nodes:
            if CycleValidator._get_cycled_nodes_recursive(node, node_status, cycle_detected, ordered_nodes):
                return cycle_detected, ordered_nodes

        return cycle_detected, ordered_nodes

    @staticmethod
    def _get_cycled_nodes_recursive(node: _ModuleNode, status_dict: dict, cycle_detected: list, ordered_nodes: list):
        status = status_dict.get(node.node_id)
        if status == _NodeStatus.VISITED_IN_CUR_PATH:
            return True
        if status == _NodeStatus.VISITED_IN_OTHER_PATH:
            return False
        status_dict[node.node_id] = _NodeStatus.VISITED_IN_CUR_PATH
        for neighbor in node.inputs:
            cycle = CycleValidator._get_cycled_nodes_recursive(neighbor, status_dict, cycle_detected, ordered_nodes)
            if cycle:
                cycle_detected.append(node)
                return cycle
        ordered_nodes.append(node)
        status_dict[node.node_id] = _NodeStatus.VISITED_IN_OTHER_PATH
