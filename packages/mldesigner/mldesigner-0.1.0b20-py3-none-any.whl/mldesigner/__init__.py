# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

# pylint: disable=redefined-builtin
from ._compile._compile import compile
from ._component import command_component
from ._execute._execute import execute
from ._generate import generate
from ._get_io_context import IOContext, OutputContext, get_io_context
from ._get_root_pipeline_context import PipelineContext, PipelineStage, get_root_pipeline_context
from ._input_output import Input, Output, Meta
from ._reference_component import reference_component
from ._utils import check_main_package as _check_azure_ai_ml_package

__all__ = [
    "command_component",
    "Input",
    "Output",
    "Meta",
    "reference_component",
    "generate",
    "execute",
    "compile",
    "IOContext",
    "OutputContext",
    "get_io_context",
    "get_root_pipeline_context",
    "PipelineContext",
    "PipelineStage",
]


_check_azure_ai_ml_package()
