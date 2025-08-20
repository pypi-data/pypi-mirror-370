# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-name-in-module, import-error, unused-import

"""
This file stores functions and objects that will be used in mldesigner package.
DO NOT change the module names in "all" list, add new modules if needed.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

import importlib

from azure.ai.ml import (
    Input,
    MLClient,
    MpiDistribution,
    Output,
    PyTorchDistribution,
    TensorFlowDistribution,
    load_component,
    load_environment,
)
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import (
    Command,
    CommandComponent,
    Component,
    Environment,
    Parallel,
    Pipeline,
    PipelineComponent,
    PipelineJob,
    ResourceConfiguration,
    Spark,
    Sweep,
    ValidationResult,
)
from azure.ai.ml.identity import AzureMLOnBehalfOfCredential
from azure.identity import AzureCliCredential
from mldesigner._constants import MLDESIGNER_IMPORTS_MODULE

# find_spec was introduced in python 3.4
if importlib.util.find_spec(MLDESIGNER_IMPORTS_MODULE) is not None:
    from azure.ai.ml.dsl._mldesigner import (
        V1_COMPONENT_TO_NODE,
        ParallelFor,
        _generate_component_function,
        _get_param_with_standard_annotation,
        component_factory_load_from_dict,
        condition,
        do_while,
        get_ignore_file,
        group,
        parallel_for,
        try_enable_internal_components,
    )
else:
    from azure.ai.ml._internal._schema.component import NodeType as V1NodeType
    from azure.ai.ml._internal.entities import Ae365exepool
    from azure.ai.ml._internal.entities import Command as InternalCommand
    from azure.ai.ml._internal.entities import DataTransfer, Distributed, HDInsight, Hemera
    from azure.ai.ml._internal.entities import Parallel as InternalParallel
    from azure.ai.ml._internal.entities import Pipeline as InternalPipeline
    from azure.ai.ml._internal.entities import Scope, Starlite
    from azure.ai.ml._utils._asset_utils import get_ignore_file
    from azure.ai.ml._utils.utils import try_enable_internal_components
    from azure.ai.ml.dsl._condition import condition
    from azure.ai.ml.dsl._do_while import do_while
    from azure.ai.ml.dsl._group_decorator import group
    from azure.ai.ml.dsl._parallel_for import ParallelFor, parallel_for
    from azure.ai.ml.entities._component.component_factory import component_factory
    from azure.ai.ml.entities._inputs_outputs import _get_param_with_standard_annotation
    from azure.ai.ml.entities._job.pipeline._io import PipelineInput
    from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function

    V1_COMPONENT_TO_NODE = {
        V1NodeType.SCOPE: Scope,
        V1NodeType.COMMAND: InternalCommand,
        V1NodeType.PARALLEL: InternalParallel,
        V1NodeType.DATA_TRANSFER: DataTransfer,
        V1NodeType.DISTRIBUTED: Distributed,
        V1NodeType.HDI: HDInsight,
        V1NodeType.STARLITE: Starlite,
        V1NodeType.HEMERA: Hemera,
        V1NodeType.AE365EXEPOOL: Ae365exepool,
        V1NodeType.PIPELINE: InternalPipeline,
    }

    component_factory_load_from_dict = component_factory.load_from_dict

__all__ = [
    "AzureCliCredential",
    "AzureMLOnBehalfOfCredential",
    "condition",
    "Command",
    "CommandComponent",
    "Component",
    "do_while",
    "parallel_for",
    "Environment",
    "get_ignore_file",
    "group",
    "Input",
    "MLClient",
    "MpiDistribution",
    "Output",
    "Parallel",
    "Pipeline",
    "PipelineComponent",
    "PyTorchDistribution",
    "ResourceConfiguration",
    "TensorFlowDistribution",
    "V1_COMPONENT_TO_NODE",
    "ValidationResult",
    "_generate_component_function",
    "component_factory_load_from_dict",
    "load_component",
    "load_environment",
    "pipeline",
    "PipelineJob",
    "PipelineInput",
    "_get_param_with_standard_annotation",
    "Spark",
    "Sweep",
    "try_enable_internal_components",
    "ParallelFor",  # use ParallelFor._to_rest_items() to convert items to rest items
]
