# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin, protected-access

"""This file includes the type classes which could be used in mldesigner.command_component

.. note::

    The following pseudo-code shows how to create a command component with such classes.

    .. code-block:: python

        @command_component(name=f"mldesigner_component_train", display_name="my-train-job")
        def train_func(
            input_param0: Input,
            input_param1: Input(type="uri_folder", path="xxx", mode="ro_mount"),
            output_param: Output(type="uri_folder", path="xxx", mode="rw_mount"),
            int_param0: Input(type="integer", min=-3, max=10, optional=True) = 0,
            int_param1 = 2
            str_param = 'abc',
        ):
            pass

"""
from collections import OrderedDict
from enum import EnumMeta
from inspect import Parameter, signature
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union, overload

from typing_extensions import Literal

from mldesigner._constants import IoConstants, RunHistoryOperations
from mldesigner._exceptions import UserErrorException
from mldesigner._logger_factory import _LoggerFactory
from mldesigner._utils import _get_annotation_by_value, _get_annotation_cls_by_type, _write_properties_to_run_history

logger = _LoggerFactory.get_logger("input_output", target_stdout=True)


# TODO: merge with azure.ai.ml.entities.Input/Output
class _IOBase:
    """Define the base class of Input/Output/Parameter class."""

    def __init__(self, port_name=None, type=None, description=None, **kwargs):
        """Define the basic properties of io definition."""
        self._port_name = port_name
        self.type = type
        self.description = description
        # record extra kwargs and pass to azure.ai.ml.entities.Input/Output for forward compatibility
        self._kwargs = kwargs or {}


class Input(_IOBase):
    """Define an input of a component.

    Default to be a uri_folder Input.

    :param type: The type of the data input. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model',
                        'integer', 'number', 'string', 'boolean'
    :type type: str
    :param path: The path to which the input is pointing. Could be local data, cloud data, a registered name, etc.
    :type path: str

    :param mode: The mode of the data input. Possible values are:
                        'ro_mount': Read-only mount the data,
                        'download': Download the data to the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
    :type min: Union[integer, float]
    :param max: The max value -- if a larger value is passed to a job, the job execution will fail
    :type max: Union[integer, float]
    :param optional: Determine if this input is optional
    :type optional: bool
    :param description: Description of the input
    :type description: str
    """

    _EMPTY = Parameter.empty
    _IO_KEYS = ["path", "type", "mode", "description", "min", "max", "enum", "optional", "default"]

    @overload
    def __init__(
        self,
        *,
        type: Literal[
            "uri_folder",
            "uri_file",
            "mltable",
            "mlflow_model",
            "custom_model",
            "integer",
            "number",
            "string",
            "boolean",
        ] = "uri_folder",
        path: str = None,
        mode: str = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize an input of a component.

        :param path: The path to which the input is pointing. Could be local data, cloud data, a registered name, etc.
        :type path: str
        :param type: The type of the data input. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data input. Possible values are:
                            'ro_mount': Read-only mount the data,
                            'download': Download the data to the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["number"] = "number",
        min: float = None,
        max: float = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a number input

        :param type: The type of the data input. Can only be set to "number".
        :type type: str
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: float
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: float
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["integer"] = "integer",
        min: int = None,
        max: int = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize an integer input

        :param type: The type of the data input. Can only be set to "integer".
        :type type: str
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: integer
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: integer
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["string"] = "string",
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a string input.

        :param type: The type of the data input. Can only be set to "string".
        :type type: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["boolean"] = "boolean",
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a bool input.

        :param type: The type of the data input. Can only be set to "boolean".
        :type type: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = None,
        min: Union[int, float] = None,
        max: Union[int, float] = None,
        enum=None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        # As an annotation, it is not allowed to initialize the _port_name.
        # The _port_name will be updated by the annotated variable name.
        self._is_primitive_type = type in IoConstants.PRIMITIVE_STR_2_TYPE
        self.path = path
        self.mode = None if self._is_primitive_type else mode
        self.min = min
        self.max = max
        self.enum = enum
        self.optional = optional
        self.default = kwargs.pop("default", None)
        super().__init__(port_name=None, type=type, description=description, **kwargs)
        # normalize properties like ["default", "min", "max", "optional"]
        self._normalize_self_properties()

    def _to_io_entity_args_dict(self):
        """Convert the Input object to a kwargs dict for azure.ai.ml.entity.Input."""
        keys = self._IO_KEYS
        result = {key: getattr(self, key, None) for key in keys}
        result = {**self._kwargs, **result}
        return _remove_empty_values(result)

    @classmethod
    def _get_input_by_type(cls, t: type, optional=None):
        if t in IoConstants.PRIMITIVE_TYPE_2_STR:
            return cls(type=IoConstants.PRIMITIVE_TYPE_2_STR[t], optional=optional)
        return None

    @classmethod
    def _get_default_unknown_input(cls, optional=None):
        # Set type as None here to avoid schema validation failed
        return cls(type=None, optional=optional)

    def _normalize_self_properties(self):
        # parse value from string to it's original type. eg: "false" -> False
        if self.type in IoConstants.PARAM_PARSERS:
            for key in ["default", "min", "max"]:
                if getattr(self, key) is not None:
                    origin_value = getattr(self, key)
                    new_value = IoConstants.PARAM_PARSERS[self.type](origin_value)
                    setattr(self, key, new_value)
        self.optional = IoConstants.PARAM_PARSERS["boolean"](getattr(self, "optional", "false"))
        self.optional = True if self.optional is True else None


class Output(_IOBase):
    """Define an output of a component.

    :param type: The type of the data output. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
    :type type: str
    :param path: The path to which the output is pointing. Needs to point to a cloud path.
    :type path: str
    :param mode: The mode of the data output. Possible values are:
                        'rw_mount': Read-write mount the data,
                        'upload': Upload the data from the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param description: Description of the output
    :type description: str
    """

    _IO_KEYS = ["path", "type", "mode", "description", "early_available"]

    @overload
    def __init__(
        self,
        *,
        type: Literal[
            "uri_folder",
            "uri_file",
            "mltable",
            "mlflow_model",
            "custom_model",
            "integer",
            "number",
            "string",
            "boolean",
        ] = "uri_folder",
        path=None,
        mode=None,
        description=None,
        early_available=None,
    ):
        """Define an output of a component.

        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        :param early_available: Determine the Output is early available or not.
        :type early_available: bool
        """

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path=None,
        mode=None,
        description=None,
        early_available=None,
        **kwargs,
    ):
        # As an annotation, it is not allowed to initialize the _port_name.
        # The _port_name will be updated by the annotated variable name.
        self.path = path
        self.mode = mode
        self.early_available = early_available
        super().__init__(port_name=None, type=type, description=description, **kwargs)
        self._is_primitive_type = self.type in IoConstants.PRIMITIVE_STR_2_TYPE
        # early available output value and ready flag
        self._value = None
        self._ready = None

    def _to_io_entity_args_dict(self):
        """Convert the Output object to a kwargs dict for azure.ai.ml.entity.Output."""
        keys = self._IO_KEYS
        result = {key: getattr(self, key) for key in keys}
        result.update(self._kwargs)
        return _remove_empty_values(result)

    def ready(self) -> None:
        """Mark early available output ready."""
        execute_logger = _LoggerFactory.get_logger("execute", target_stdout=True)
        # validate
        if self._ready is True:
            execute_logger.warning(
                "Output '%s' has already been marked as ready, ignore current operation.", self._port_name
            )
            return
        if self._value is None:
            error_message = f"Early available output {self._port_name!r} is not ready yet, please assign value for it."
            raise UserErrorException(error_message)
        # validate AzureML limits (https://aka.ms/azure-machine-learning-limits),
        # length of property key (100 characters) and length of property value (1000 characters).
        # note that we have prefix (azureml.pipeline.control.) in key, so there are 75 characters left.
        if len(self._port_name) > 75:
            error_message = (
                f"Early available output {self._port_name!r} port name is too long, the limit is 75 characters."
            )
            raise UserErrorException(error_message)
        if isinstance(self._value, str) and len(self._value) > 1000:
            error_message = (
                f"Early available output {self._port_name!r} content is too long, the limit is 1000 characters. "
                f"Got {len(self._value)} characters, please control the size."
            )
            raise UserErrorException(error_message)

        # write content to uri_file
        from mldesigner._component_executor import _parsed_args

        # if component is executed without mldesigner, cannot know where is the target file
        if _parsed_args is not None:
            execute_logger.info("Write early available output content '%s' to file", self._value)
            Path(_parsed_args[self._port_name]).write_text(str(self._value))

        # write content to RH
        early_available_control_output_key = f"azureml.pipeline.control.{self._port_name}"
        _write_properties_to_run_history(
            properties={early_available_control_output_key: self._value},
            operation_name=RunHistoryOperations.MARK_OUTPUT_READY,
        )
        self._ready = True


def _remove_empty_values(data, ignore_keys=None):
    if not isinstance(data, dict):
        return data
    ignore_keys = ignore_keys or {}
    return {
        k: v if k in ignore_keys else _remove_empty_values(v)
        for k, v in data.items()
        if v is not None or k in ignore_keys
    }


def _standalone_get_param_with_standard_annotation(func):
    """Parse annotations for standalone mode func"""

    def _get_fields(annotations):
        """Return field names to annotations mapping in class."""
        annotation_fields = OrderedDict()
        for name, annotation in annotations.items():
            # Skip return type
            if name == "return":
                continue
            # Handle EnumMeta annotation
            if isinstance(annotation, EnumMeta):
                annotation = String(enum=annotation)
            # Try creating annotation by type when got like 'param: int'
            if not _is_mldesigner_type_cls(annotation) and not _is_mldesigner_types(annotation):
                annotation = _get_annotation_cls_by_type(annotation, raise_error=False, is_dependency=False)
                if not annotation:
                    # Fall back to default unknown parameter
                    annotation = Input._get_default_unknown_input()
            annotation_fields[name] = annotation
        return annotation_fields

    def _merge_field_keys(annotation_fields, defaults_dict):
        """Merge field keys from annotations and cls dict to get all fields in class."""
        anno_keys = list(annotation_fields.keys())
        dict_keys = defaults_dict.keys()
        if not dict_keys:
            return anno_keys
        return [*anno_keys, *[key for key in dict_keys if key not in anno_keys]]

    def _update_annotation_with_default(anno, name, default):
        """Create annotation if is type class and update the default."""
        # Create instance if is type class
        complete_annotation = anno
        if _is_mldesigner_type_cls(anno):
            complete_annotation = anno()
        complete_annotation._port_name = name
        if default is Input._EMPTY:
            return complete_annotation
        if isinstance(complete_annotation, Input) and complete_annotation._is_primitive_type:
            # For mldesigner Input, user cannot set default inside Input class,
            # instead it's set by "=" as parameter default
            # As mldesigner Input is merely an interface, there is no validation for default value yet
            complete_annotation.default = default
        elif isinstance(complete_annotation, _Param):
            # Set default value to primitive type in mldesigner
            complete_annotation._default = default
        return complete_annotation

    def _merge_and_update_annotations(annotation_fields, defaults_dict):
        """Use public values in class dict to update annotations."""
        all_fields = OrderedDict()
        all_filed_keys = _merge_field_keys(annotation_fields, defaults_dict)
        for name in all_filed_keys:
            # Get or create annotation
            annotation = (
                annotation_fields[name]
                if name in annotation_fields
                else _get_annotation_by_value(defaults_dict.get(name, Input._EMPTY))
            )
            # Create annotation if is class type and update default
            annotation = _update_annotation_with_default(annotation, name, defaults_dict.get(name, Input._EMPTY))
            all_fields[name] = annotation
        return all_fields

    annotations = getattr(func, "__annotations__", {})
    annotation_fields = _get_fields(annotations)
    defaults_dict = {
        key: val.default
        for key, val in signature(func).parameters.items()
        if val.kind not in [val.VAR_POSITIONAL, val.VAR_KEYWORD]
    }
    all_fields = _merge_and_update_annotations(annotation_fields, defaults_dict)
    return all_fields


def _is_mldesigner_type_cls(t: type):
    if not isinstance(t, type):
        return False
    return issubclass(t, (Input, Output, _Param))


def _is_mldesigner_types(o: object):
    return _is_mldesigner_type_cls(type(o))


class _Param(_IOBase):
    """This is the base class of component primitive types Inputs/Outputs.

    The properties including type/options/optional/min/max will be dumped in component spec.
    """

    DATA_TYPE = None  # This field is the corresponding python type of the class, e.g. str/int/float.
    TYPE_NAME = None  # This field is the type name of the parameter, e.g. string/integer/number.

    def __init__(
        self,
        description=None,
        optional=None,
        min=None,
        max=None,
        enum=None,
        **kwargs,
    ):
        """Define a parameter of a component."""
        super().__init__(port_name=None, type=self.TYPE_NAME, description=description)
        self._optional = optional
        self._min = min
        self._max = max
        self._enum = enum
        self._is_primitive_type = self.TYPE_NAME in IoConstants.PRIMITIVE_STR_2_TYPE
        self._default = kwargs.pop("default", None)

    def _to_io_entity_args_dict(self):
        """Convert the object to a kwargs dict for azure.ai.ml.entity.Output."""
        keys = ["type", "optional", "min", "max", "enum", "description", "default"]
        result = {key: getattr(self, key, None) for key in keys}
        result.update(self._kwargs)
        return _remove_empty_values(result)

    def _is_enum(self):
        """returns true if the param is enum."""
        return self.type == String.TYPE_NAME and self.enum

    @property
    def optional(self) -> bool:
        """Return whether the parameter is optional."""
        return self._optional

    @property
    def max(self) -> Optional[Union[int, float]]:
        """Return the maximum value of the parameter for a numeric parameter."""
        return self._max

    @property
    def min(self) -> Optional[Union[int, float]]:
        """Return the minimum value of the parameter for a numeric parameter."""
        return self._min

    @property
    def enum(self) -> Optional[Union[EnumMeta, Sequence[str]]]:
        """Return the enum list of the parameter for a string parameter."""
        return self._enum

    @property
    def default(self):
        """Return the default value of the parameter."""
        return self._default


class String(_Param):
    """String parameter passed the parameter string with its raw value."""

    DATA_TYPE = str
    TYPE_NAME = "string"

    def __init__(
        self,
        description=None,
        optional=None,
        enum=None,
        **kwargs,
    ):
        """Initialize a string parameter.

        :param description: Description of the param.
        :type description: str
        :param optional: If the param is optional.
        :type optional: bool
        """
        if enum:
            enum_values = self._assert_enum_valid(enum)
            # This is used to parse enum class instead of enum str value if a enum class is provided.
            if isinstance(enum, EnumMeta):
                self._enum_class = enum
                self._str2enum = dict(zip(enum_values, enum))
            else:
                self._enum_class = None
                self._str2enum = {v: v for v in enum_values}
        else:
            enum_values = None
        _Param.__init__(self, description=description, optional=optional, enum=enum_values)

    @property
    def default(self):
        return self._parse_enum(self._default)

    def _parse_enum(self, val: str):
        """Parse the enum value from a string value or the enum value."""
        if val is None:
            return val

        if self._enum_class and isinstance(val, self._enum_class):
            return val.value

        if val not in self._str2enum:
            msg = "Not a valid enum value: '{}', valid values: {}"
            raise UserErrorException(
                message=msg.format(val, ", ".join(self.enum)),
            )
        return self._str2enum[val].value

    @classmethod
    def _assert_enum_valid(cls, enum):
        """Check whether the enum is valid and return the values of the
        enum."""
        if isinstance(enum, EnumMeta):
            enum_values = [str(option.value) for option in enum]
        elif isinstance(enum, Iterable):
            enum_values = list(enum)
        else:
            raise UserErrorException("enum must be a subclass of Enum or an iterable.")

        if len(enum_values) <= 0:
            raise UserErrorException("enum must have enum values.")

        if any(not isinstance(v, str) for v in enum_values):
            raise UserErrorException(
                message="enum values must be str type.",
            )

        return enum_values


class _Numeric(_Param):
    """Numeric Parameter is an intermediate type which is used to validate the value according to min/max."""

    def _validate_or_throw(self, val):
        if self._min is not None and val < self._min:
            raise ValueError("Parameter '%s' should not be less than %s." % (self._port_name, self._min))
        if self._max is not None and val > self._max:
            raise ValueError("Parameter '%s' should not be greater than %s." % (self._port_name, self._max))


class Integer(_Numeric):
    """Int Parameter parse the value to a int value."""

    DATA_TYPE = int
    TYPE_NAME = "integer"

    def __init__(
        self,
        min=None,
        max=None,
        description=None,
        optional=None,
        **kwargs,
    ):
        """Initialize an integer parameter.

        :param min: Minimal value of the param.
        :type min: int
        :param max: Maximum value of the param.
        :type max: int
        :param description: Description of the param.
        :type description: str
        :param optional: If the param is optional.
        :type optional: bool
        """
        _Numeric.__init__(
            self,
            optional=optional,
            description=description,
            min=min,
            max=max,
            **kwargs,
        )


class Number(_Numeric):
    """Float Parameter parse the value to a float value."""

    DATA_TYPE = float
    TYPE_NAME = "number"

    def __init__(
        self,
        min=None,
        max=None,
        description=None,
        optional=None,
        **kwargs,
    ):
        """Initialize a float parameter.

        :param min: Minimal value of the param.
        :type min: float
        :param max: Maximum value of the param.
        :type max: float
        :param description: Description of the param.
        :type description: str
        :param optional: If the param is optional.
        :type optional: bool
        """
        _Numeric.__init__(
            self,
            optional=optional,
            description=description,
            min=min,
            max=max,
            **kwargs,
        )


class Boolean(_Param):
    """Bool Parameter parse the value to a bool value."""

    DATA_TYPE = bool
    TYPE_NAME = "boolean"

    def __init__(
        self,
        description=None,
        optional=None,
        **kwargs,
    ):
        """Initialize a bool parameter.

        :param description: Description of the param.
        :type description: str
        :param optional: If the param is optional.
        :type optional: bool
        """
        _Param.__init__(
            self,
            optional=optional,
            description=description,
            **kwargs,
        )


class Meta(object):
    """This is the meta data of Inputs/Outputs."""

    def __init__(
        self,
        type=None,
        description=None,
        min=None,
        max=None,
        **kwargs,
    ):
        self.type = type
        self.description = description
        self._min = min
        self._max = max
        self._default = kwargs.pop("default", None)
        self._kwargs = kwargs

    def _to_io_entity_args_dict(self):
        """Convert the object to a kwargs dict for azure.ai.ml.entity.Output."""
        keys = set(Output._IO_KEYS + Input._IO_KEYS)
        result = {key: getattr(self, key, None) for key in keys}
        result.update(self._kwargs)
        if IoConstants.PRIMITIVE_TYPE_2_STR.get(self.type) is not None:
            result["type"] = IoConstants.PRIMITIVE_TYPE_2_STR.get(self.type)
        return _remove_empty_values(result)

    @property
    def max(self) -> Optional[Union[int, float]]:
        """Return the maximum value of the parameter for a numeric parameter."""
        return self._max

    @property
    def min(self) -> Optional[Union[int, float]]:
        """Return the minimum value of the parameter for a numeric parameter."""
        return self._min

    @property
    def default(self):
        """Return the default value of the parameter."""
        return self._default
