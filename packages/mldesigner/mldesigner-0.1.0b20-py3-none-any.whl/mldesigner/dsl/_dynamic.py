# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, unused-argument
import copy
import functools
import inspect
from os import PathLike
from pathlib import Path
from typing import Any, Callable, TypeVar, Union

from mldesigner._component import _create_executor, _update_executor_inputs_by_values, _validate_component_name
from mldesigner._constants import ExecutorTypes
from mldesigner._utils import _resolve_source_directory

_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])
SPEC_EXT = ".spec.yaml"


def dynamic(
    func=None,
    *,
    name=None,
    version=None,
    display_name=None,
    description=None,
    is_deterministic=None,
    tags=None,
    environment: Union[str, dict, PathLike, "Environment"] = None,
    code: Union[str, PathLike] = None,
):
    """Return a decorator which is used to declare a dynamic pipeline with @dynamic.

    Dynamic pipeline has same interface as a command_component but works like a pipeline.
    It will collect all nodes created inside it and built a pipeline component.
    Note: Pipeline meta like default_compute is not recommended practice.

    .. note::

        The following example shows how to use @dynamic to declare a simple component.

        .. code-block:: python

            @dynamic
            def dynamic_subgraph(input: Input(type=""), str_param='str_param'):
                # the following nodes will be created directly
                with open(input) as file:
                    nodes = json.load(file)
                    for node in nodes:
                        dummy_component(str_param=str_param)


    :param func: The user component function to be decorated.
    :param func: types.FunctionType
    :param name: The name of the component. If None is set, function name is used.
    :type name: str
    :param version: Version of the component. If not specified, the version will be auto-incremented.
    :type version: str
    :param display_name: Display name of the component.
    :type display_name: str
    :param description: The description of the component. If None is set, the doc string is used.
    :type description: str
    :param is_deterministic: Specify whether the component will always generate the same result. The default value is
                             None, the component will be reused by default behavior, the same for True value. If
                             False, this component will never be reused.
    :type is_deterministic: bool
    :param tags: Tags of the component.
    :type tags: dict
    :param environment: Environment config of component, could be a yaml file path, a dict or an Environment object.
                        If None, a default conda with 'azure-ai-ml' will be used.
    :type environment: Union[str, os.PathLike, dict, azure.ai.ml.entities.Environment]
    :param code: The source directory of component, with default value '.'.
                 i.e. The directory of mldesigner component file.
    :type code: Union[str, PathLike]
    :return: The decorated function which could be used to create component directly.
    """
    # import here to make sure dsl.dynamic can be exposed without azure-ai-ml
    # but will raise error when used without azure-ai-ml
    from mldesigner.dsl._dynamic_executor import DynamicExecutor

    _validate_component_name(name=name)

    # Get the directory of decorator to resolve absolute code path in environment
    # Note: The decorator defined source directory may be different from mldesigner component source directory.
    decorator_defined_source_dir = _resolve_source_directory()
    # If is in mldesigner component execution process, skip resolve file path.
    EXECUTOR_CLASS = DynamicExecutor
    environment = EXECUTOR_CLASS._refine_environment(environment, decorator_defined_source_dir)
    if code:
        # Resolve code source immediately if defined with code.
        code = Path(decorator_defined_source_dir / code).resolve().absolute().as_posix()

    entity_args = {k: v for k, v in locals().items() if v is not None and k in inspect.signature(dynamic).parameters}

    # func is not necessary for component entity
    entity_args.pop("func", None)

    # pylint: disable=isinstance-second-argument-not-valid-type
    def component_func_decorator(func: _TFunc) -> _TFunc:
        nonlocal entity_args

        executor, raw_func, entity_args = _create_executor(
            EXECUTOR_CLASS=EXECUTOR_CLASS, func=func, code=code, entity_args=entity_args
        )

        _component_func = None

        @functools.wraps(raw_func)
        def wrapper(*args, **kwargs):
            nonlocal _component_func, executor
            if executor._is_variable_inputs:
                variable_inputs_executor = copy.copy(executor)
                variable_inputs_executor, func_kwargs = _update_executor_inputs_by_values(
                    kwargs, raw_func, variable_inputs_executor
                )
                # Convert inputs to key-value dict.
                variable_inputs_component_func = EXECUTOR_CLASS._get_generate_component_function(
                    variable_inputs_executor.component
                )
                return variable_inputs_component_func(*args, **func_kwargs)  # pylint: disable=not-callable
            if not _component_func:
                _component_func = EXECUTOR_CLASS._get_generate_component_function(executor.component)
            return _component_func(*args, **kwargs)  # pylint: disable=not-callable

        wrapper._is_mldesigner_component = True
        wrapper._executor = executor
        wrapper._type = ExecutorTypes.DYNAMIC

        wrapper.component = executor.component

        return wrapper

    # enable using decorator without "()" if all arguments are default values
    if func is not None:
        return component_func_decorator(func)
    return component_func_decorator
