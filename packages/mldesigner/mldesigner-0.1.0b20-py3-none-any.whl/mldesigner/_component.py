# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, unused-argument

import copy
import functools
import inspect
from collections import OrderedDict
from os import PathLike
from pathlib import Path
from typing import Any, Callable, TypeVar, Union

from mldesigner._component_executor import ComponentExecutor, ExecutorBase
from mldesigner._exceptions import ComponentDefiningError
from mldesigner._utils import (
    _copy_func,
    _get_annotation_by_value,
    _is_instance_of,
    _relative_to,
    _resolve_source_directory,
    _resolve_source_file,
    is_valid_name,
)

# hint vscode intellisense
_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])
SPEC_EXT = ".spec.yaml"


def _validate_component_name(name: str):
    if name and not is_valid_name(name):
        msg = "Name is not valid, it could only contains a-z, A-Z, 0-9 and '.-_', got '%s'." % name
        raise ComponentDefiningError(name, msg)


def _create_executor(EXECUTOR_CLASS, func, code, entity_args):
    # pylint: disable=isinstance-second-argument-not-valid-type
    if not isinstance(func, Callable):
        raise ComponentDefiningError(
            name=None,
            cause=f"Mldesigner component decorator accept only function type, got {type(func)}.",
        )
    return_annotation = EXECUTOR_CLASS._get_outputs_from_return_annotation(func=func)
    # if contains control/early available output(s), force inject dependencies into component environment
    force_inject_deps = EXECUTOR_CLASS._require_deps_injection(func=func)

    entity_args = EXECUTOR_CLASS._refine_entity_args(entity_args, return_annotation, force_inject_deps)

    entity_args["name"] = entity_args.get("name", func.__name__)
    entity_args["display_name"] = entity_args.get("display_name", entity_args["name"])
    entity_args["description"] = entity_args.get("description", func.__doc__)
    # pop description if not set, otherwise it's None value and will raise error when load schema
    if entity_args["description"] is None:
        entity_args.pop("description")
    func_entry_path = _resolve_source_file()
    if not func_entry_path:
        func_entry_path = Path(inspect.getfile(func)).resolve().absolute()
        # if component defined in a .ipynb the path is a pseudo path and it will interfere component entity
        # generation or component compile
        if not Path(func_entry_path).exists():
            msg = (
                f"Component source path not found: '{func_entry_path}'. If the component is defined inside "
                f"'.ipynb' please try to define it in a separate '.py' file."
            )
            raise ComponentDefiningError(entity_args["name"], msg)

    # Fall back to func entry directory if not specified.
    entity_args["source_path"] = str(func_entry_path)
    entity_args["code"] = entity_args.pop("code") if code else Path(func_entry_path).parent.absolute().as_posix()

    # Set entry name as relative path to code
    entry_relative_path = _relative_to(func_entry_path, entity_args["code"])
    if not entry_relative_path:
        raise ComponentDefiningError(
            name=entity_args["name"],
            cause=(
                f"Mldesigner component {entity_args['name']!r} source directory {func_entry_path!r} "
                f"not under code directory {entity_args['code']!r}"
            ),
        )
    entry_relative_path = entry_relative_path.as_posix()
    entity_args["command"] = [
        "mldesigner",
        "execute",
        "--source",
        str(entry_relative_path),
        "--name",
        entity_args["name"],
    ]
    # Initialize a ComponentExecutor to make sure it works and use it to update the component function.
    # Save the raw func as we will wrap it
    raw_func = _copy_func(func)

    executor = EXECUTOR_CLASS(func=raw_func, entity_args=entity_args, _entry_file=func_entry_path)
    executor._update_func(raw_func)
    return executor, raw_func, entity_args


def command_component(
    func=None,
    *,
    name=None,
    version=None,
    display_name=None,
    description=None,
    is_deterministic=None,
    tags=None,
    environment: Union[str, dict, PathLike, "Environment"] = None,
    distribution: Union[dict, "PyTorchDistribution", "MpiDistribution", "TensorFlowDistribution"] = None,
    resources: Union[dict, "ResourceConfiguration"] = None,
    code: Union[str, PathLike] = None,
):
    """Return a decorator which is used to declare a component with @command_component.

    A component is a reusable unit in an Azure Machine Learning workspace.
    With the decorator @command_component, a function could be registered as a component in the workspace.
    Then the component could be used to construct an Azure Machine Learning pipeline.

    .. note::

        The following example shows how to use @command_component to declare a simple component.

        .. code-block:: python

            @command_component()
            def your_component_function(output:Output(), input: Input(), param='str_param'):
                pass

        The following example shows how to declare a component with detailed meta data.

        .. code-block:: python

            @command_component(name=name, version=version, description=description)
            def your_component_function(output: Output(), input: Input(), param='str_param'):
                pass

        The following example shows how to consume the declared component function with dsl.pipeline.

        .. code-block:: python

            from azure.ai.ml import MLClient
            from azure.ai.ml.dsl import pipeline

            # define pipeline with mldesigner.command_component function
            @pipeline()
            def your_pipeline_func(input, param):
                your_component_function(input=input, param=param)

            # create the pipeline
            pipeline = your_pipeline_func(your_input, 'your_str')

            # Submit pipeline through MLClient

            ml_client = MLClient(cred, "my-sub", "my-rg", "my-ws")
            ml_client.create_or_update(pipeline)

    :param func: The user component function to be decorated.
    :type func: types.FunctionType
    :param name: The name of the component. If None is set, function name is used.
    :type name: str
    :param version: Version of the component.
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
    :param distribution: The distribution config of component, e.g. distribution={'type': 'mpi'}.
    :type distribution: Union[dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution]
    :param resources: Compute Resource configuration for the component.
    :type resources: Union[dict, ResourceConfiguration]
    :param code: The source directory of component, with default value '.'.
                 i.e. The directory of mldesigner component file.
    :type code: Union[str, PathLike]
    :return: The decorated function which could be used to create component directly.
    """

    _validate_component_name(name=name)

    # Get the directory of decorator to resolve absolute code path in environment
    # Note: The decorator defined source directory may be different from mldesigner component source directory.
    decorator_defined_source_dir = _resolve_source_directory()
    # If is in mldesigner component execution process, skip resolve file path.
    EXECUTOR_CLASS = ExecutorBase._get_executor_class()
    environment = EXECUTOR_CLASS._refine_environment(environment, decorator_defined_source_dir)
    if code:
        # Resolve code source immediately if defined with code.
        code = Path(decorator_defined_source_dir / code).resolve().absolute().as_posix()

    entity_args = {
        k: v for k, v in locals().items() if v is not None and k in inspect.signature(command_component).parameters
    }

    # func is not necessary for component entity
    entity_args.pop("func", None)

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
                if EXECUTOR_CLASS == ComponentExecutor:
                    # Convert inputs to key-value dict.
                    variable_inputs_dict = (
                        inspect.signature(variable_inputs_executor._func).bind_partial(*args, **kwargs).arguments
                    )
                    kwargs_param = next(
                        filter(
                            lambda param: param.kind in [param.VAR_KEYWORD],
                            inspect.signature(variable_inputs_executor._func).parameters.values(),
                        )
                    )
                    inputs_kwargs = variable_inputs_dict.pop(kwargs_param.name, {})
                    variable_inputs_dict.update(inputs_kwargs)
                    variable_inputs_executor._execution_args = dict(variable_inputs_dict)
                    return variable_inputs_executor

                _variable_inputs_component_func = EXECUTOR_CLASS._get_generate_component_function(
                    variable_inputs_executor.component
                )
                return _variable_inputs_component_func(*args, **func_kwargs)  # pylint: disable=not-callable

            if not _component_func:
                _component_func = (
                    # If used in standalone mode, return the executor, otherwise return a component function.
                    executor
                    if EXECUTOR_CLASS == ComponentExecutor
                    else EXECUTOR_CLASS._get_generate_component_function(executor.component)
                )
            return _component_func(*args, **kwargs)

        wrapper._is_mldesigner_component = True
        wrapper._executor = executor
        if EXECUTOR_CLASS != ComponentExecutor:
            wrapper.component = executor.component
        return wrapper

    # enable using decorator without "()" if all arguments are default values
    if func is not None:
        return component_func_decorator(func)
    return component_func_decorator


def _update_executor_inputs_by_values(kwargs, func, executor):
    """Update execute inputs by the func kwargs and
    return the updated executor and the key-value of func inputs."""
    args_mapping, func_kwargs = OrderedDict(executor._arg_mapping), {}
    parameters = inspect.signature(func).parameters

    # Generate input mapping by kwargs, the input name is the key.
    var_kwarg = next((param for param in parameters.values() if param.kind == param.VAR_KEYWORD), None)
    for k, v in kwargs.items():
        if k in executor._arg_mapping:
            args_mapping[k] = executor._arg_mapping[k]
        elif not var_kwarg:
            raise ComponentDefiningError(executor._entity_args["name"], "Component does not support variable kwargs.")
        else:
            data = v
            if not isinstance(executor, ComponentExecutor):
                while _is_instance_of(data, "PipelineInput"):
                    data = data._data
                annotation = _get_annotation_by_value(data, is_dependency=True)

                if _is_instance_of(data, "Input"):
                    annotation.type = data.type
                elif _is_instance_of(data, "NodeOutput"):
                    # Get the output type of the node connect to the component.
                    annotation.type = data.type
            else:
                annotation = _get_annotation_by_value(data, is_dependency=False)
            args_mapping[k] = annotation
        func_kwargs[k] = v
    executor._arg_mapping = args_mapping
    return executor, func_kwargs
