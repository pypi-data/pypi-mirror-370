# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from mldesigner._exceptions import UserErrorException

from ._condition_output import _condition_output as condition_output

try:
    from mldesigner._azure_ai_ml import ParallelFor, condition, do_while, group, parallel_for
except ImportError as e:
    err_msg = f"Please install extra dependencies by running `pip install azure-ai-ml`, currently got {e}"
    raise UserErrorException(err_msg)
from ._dynamic import dynamic

__all__ = [
    "do_while",
    "condition",
    "condition_output",  # pylint: disable=naming-mismatch
    "dynamic",
    "group",
    "parallel_for",
    "ParallelFor",
]
