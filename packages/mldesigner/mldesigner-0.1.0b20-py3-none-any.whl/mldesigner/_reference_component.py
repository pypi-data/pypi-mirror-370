# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin, unused-argument

from functools import wraps
from os import PathLike
from pathlib import Path
from typing import Any, Callable, TypeVar, Union, get_type_hints

from mldesigner._utils import _assert_arg_valid, _convert_internal_type, _detect_output_types

_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])

DEFAULT_COMPONENT_LOADER_CONFIG_PATH = Path(".").parent / "components.yaml"


def reference_component(path: Union[PathLike, str] = None, name=None, version=None, registry=None, **kwargs) -> _TFunc:
    """Reference an existing component with a function and return a component node built with given params.
    The referenced component can be defined with local yaml file or in remote with name and version.
    The returned component node type are hint with function return annotation and default to Command.
    If the referenced component is local component, it'll be registered as anonymous component in pipeline's workspace.
    If the referenced component is workspace component, we assume it has been registered in pipeline's workspace.
    If the referenced component is registry component, it'll still be referenced from registry in pipeline.

    Eg: Both
    .. code-block:: python

        @reference_component()
        def my_func():
            ...
    and
    .. code-block:: python

        @reference_component()
        def my_func() -> Command:
            ...
    with return a Command node.
    .. code-block:: python

        @reference_component()
        def my_func() -> Parallel:
            ...
    will return a Parallel node.

    :param path: Path to local component file.
    :type path: str
    :param name: Name of component to load.
    :type name: str
    :param version: Version of component to load.
    :type version: str
    :param registry: Registry of component's source. None means it's not a registry component.
    :type registry: str

    :return: Component node.
    :rtype: Union[Command, Parallel]
    """

    def component_decorator(func: _TFunc) -> _TFunc:
        @wraps(func)
        def wrapper(*args, **inner_kwargs):
            from mldesigner._azure_ai_ml import Command
            from mldesigner._component_loader import ComponentLoader, ComponentsConfig
            from mldesigner._exceptions import UserErrorException
            from mldesigner._generate._generators._constants import COMPONENT_TO_NODE

            if args:
                raise UserErrorException(
                    message="`reference_component` wrapped function only accept keyword parameters."
                )
            # handle params case insensitively, raise error when unknown kwargs are passed
            _assert_arg_valid(inner_kwargs, func.__code__.co_varnames, func_name=func.__name__)

            # currently component loader only support load 1 component in reference_component
            # create a component loader only contain 1 component config with function name as key
            component_loader = ComponentLoader(
                components_config=ComponentsConfig.create_single_component_config(
                    key=func.__name__, path=path, name=name, version=version, registry=registry
                ),
                default_component_loader_config_path=DEFAULT_COMPONENT_LOADER_CONFIG_PATH,
            )

            component = component_loader.load_component(name=func.__name__)

            if hasattr(component, "type") and component.type in COMPONENT_TO_NODE:
                node = component(**inner_kwargs)
            else:
                result_cls = get_type_hints(func).get("return", Command)
                # Get component outputs
                result_properties = get_type_hints(result_cls)
                outputs = {}
                if "outputs" in result_properties:
                    from mldesigner._azure_ai_ml import Output

                    outputs_cls = get_type_hints(result_cls)["outputs"]
                    # Get output type by source code.
                    output_types = {k: _convert_internal_type(v) for k, v in _detect_output_types(outputs_cls)}
                    annotation_outputs = get_type_hints(outputs_cls)
                    outputs = {k: Output(type=output_types.get(k, None)) for k, v in annotation_outputs.items()}

                # supported return annotations, traverse in order
                # Note: make sure no base node in supported_cls
                supported_cls = COMPONENT_TO_NODE.values()
                for cls in supported_cls:
                    if issubclass(result_cls, cls):
                        result_cls = cls
                if result_cls not in supported_cls:
                    msg = (
                        f"Return annotation of `reference_component` wrapped function can only be {supported_cls} "
                        f"or its subclass, got {result_cls} instead."
                    )
                    raise UserErrorException(message=msg)

                # This node will be init with inner_kwargs and push to pipeline stack
                node = result_cls(component=component, inputs=inner_kwargs, outputs=outputs, _from_component_func=True)

                # Update remote component output types
                if name and version:
                    for output_name, output in node.outputs.items():
                        if output_name in outputs:
                            # TODO enable update primitive type output
                            output.type = outputs[output_name].type

            node = component_loader.apply_post_load_func(node=node)

            return node

        return wrapper

    return component_decorator
