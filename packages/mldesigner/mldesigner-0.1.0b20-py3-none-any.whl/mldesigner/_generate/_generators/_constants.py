# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from mldesigner._azure_ai_ml import V1_COMPONENT_TO_NODE, Command, Parallel, Pipeline, Spark
from mldesigner._constants import NodeType

V2_COMPONENT_TO_NODE = {
    NodeType.COMMAND: Command,
    NodeType.PARALLEL: Parallel,
    NodeType.SPARK: Spark,
    NodeType.PIPELINE: Pipeline,
}

COMPONENT_TO_NODE = {**V2_COMPONENT_TO_NODE, **V1_COMPONENT_TO_NODE}

NODE_TO_NAME = {}
for node in V1_COMPONENT_TO_NODE.values():
    name = node.__name__
    # Rename v1 node to avoid conflict with v2 nodes, eg: Command, Parallel
    if name in ("Command", "Parallel"):
        name = "Internal" + name
    NODE_TO_NAME[node] = name

NODE_TO_NAME.update({node: node.__name__ for node in V2_COMPONENT_TO_NODE.values()})
