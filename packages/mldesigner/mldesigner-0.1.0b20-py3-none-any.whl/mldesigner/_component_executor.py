# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes, protected-access, unused-argument

import copy
import importlib
import inspect
import json
import os
import shutil
import sys
import types
from abc import abstractmethod
from pathlib import Path
from typing import List

from typing_extensions import Annotated, get_args, get_origin

from mldesigner._constants import (
    AssetTypes,
    ComponentSource,
    CuratedEnv,
    ExecutorTypes,
    IoConstants,
    NodeType,
    RunHistoryOperations,
    SupportedParameterTypes,
)
from mldesigner._exceptions import (
    ComponentDefiningError,
    ImportException,
    NoComponentError,
    RequiredComponentNameError,
    TooManyComponentsError,
    UserErrorException,
    ValidationException,
)
from mldesigner._input_output import Input, Meta, Output, _Param, _standalone_get_param_with_standard_annotation
from mldesigner._logger_factory import _LoggerFactory
from mldesigner._utils import (
    _import_component_with_working_dir,
    _is_mldesigner_component,
    _is_variable_args_function,
    _write_properties_to_run_history,
    inject_sys_path,
    is_group,
)

execute_logger = _LoggerFactory.get_logger("execute", target_stdout=True)
# store mldesigner parsed arguments for early available output
_parsed_args = None


class ExecutorBase:
    """An executor base. Only to be inherited for sub executor classes."""

    INJECTED_FIELD = "_entity_args"  # The injected field is used to get the component spec args of the function.
    CODE_GEN_BY_KEY = "codegenBy"
    SPECIAL_FUNC_CHECKERS = {
        "Coroutine": inspect.iscoroutinefunction,
        "Generator": inspect.isgeneratorfunction,
    }
    # This is only available on Py3.6+
    if sys.version_info.major == 3 and sys.version_info.minor > 5:
        SPECIAL_FUNC_CHECKERS["Async generator"] = inspect.isasyncgenfunction
    DEFAULT_OUTPUT_NAME = "output"
    CONTROL_OUTPUTS_KEY = "azureml.pipeline.control"
    SUPPORTED_RETURN_TYPES_NON_PRIMITIVE = (Output, _Param)
    SUPPORTED_OUTPUT_METADATA = (Meta,)  # pylint: disable=invalid-name
    SUPPORTED_RETURN_TYPES_PRIMITIVE = list(IoConstants.PRIMITIVE_TYPE_2_STR.keys())
    SUPPORTED_RETURN_TYPES_ASSET = [AssetTypes.URI_FILE, AssetTypes.URI_FOLDER]
    SUPPORTED_TYPE_NAME_IN_OUTPUT_CLASS = list(SupportedParameterTypes) + SUPPORTED_RETURN_TYPES_ASSET

    def __init__(self, func: types.FunctionType, arg_mapping, entity_args=None, _entry_file=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function decorated by mldesigner.command_component.
        :type func: types.FunctionType
        :param arg_mapping: A dict mapping from parameter name to annotation.
        :type arg_mapping: dict
        :param entity_args: Component entity dict.
        :type entity_args: dict
        :param _entry_file: Component entry file path.
        :type _entry_file: str
        """
        if not isinstance(func, types.FunctionType):
            msg = "Only function type is allowed to initialize ComponentExecutor."
            raise ValidationException(message=msg)
        if entity_args is None:
            entity_args = getattr(func, self.INJECTED_FIELD, None)
            if entity_args is None:
                msg = "You must wrap the function with mldesigner component decorators before using it."
                raise ValidationException(message=msg)
        self._raw_entity_args = copy.deepcopy(entity_args)
        self._entity_args = copy.deepcopy(entity_args)
        self._name = entity_args["name"]
        self._type = entity_args.get("type", NodeType.COMMAND)
        self._entity_file_path = None
        self._assert_valid_func(func)
        self._arg_mapping = arg_mapping
        self._return_mapping = self._get_output_annotations(func=func, mapping=self._arg_mapping)
        self._execution_args = None
        self._additional_args = None  # used to notify user for additional args that are useless after execution
        self._is_variable_inputs = _is_variable_args_function(func)
        if _is_mldesigner_component(func):
            # If is mldesigner component func, set the func and entry file as original value
            self._func = func._executor._func
            self._entry_file = func._executor._entry_file
        else:
            # Else, set func directly, if _entry_file is None, resolve it from func.
            # Note: The entry file here might not equal with inspect.getfile(component._func),
            # as we can define raw func in file A and wrap it with mldesigner component in file B.
            # For the example below, we set entry file as B here (the mldesigner component defined in).
            self._func = func
            self._entry_file = _entry_file if _entry_file else Path(inspect.getfile(self._func)).absolute()

    def _assert_valid_func(self, func):
        """Check whether the function is valid, if it is not valid, raise."""
        for k, checker in self.SPECIAL_FUNC_CHECKERS.items():
            if checker(func):
                raise NotImplementedError("%s function is not supported for %s now." % (k, self._type))

    def __call__(self, *args, **kwargs):
        """Directly calling a component executor will return the executor copy with processed inputs."""
        # transform *args and **kwargs to a parameter dict
        EXECUTOR_CLASS = self._get_executor_class()
        new_executor = EXECUTOR_CLASS(func=self._func)
        new_executor._execution_args = dict(
            inspect.signature(new_executor._func).bind_partial(*args, **kwargs).arguments
        )
        return new_executor

    @classmethod
    def _collect_component_from_file(
        cls, py_file, working_dir=None, force_reload=False, component_name=None, from_executor=False
    ):
        """Collect single mldesigner component in a file and return the executors of the components."""
        py_file = Path(py_file).absolute()
        if py_file.suffix != ".py":
            msg = "{} is not a valid py file."
            raise ValidationException(message=msg.format(py_file))
        if working_dir is None:
            working_dir = py_file.parent
        working_dir = Path(working_dir).absolute()

        component_path = py_file.relative_to(working_dir).as_posix().split(".")[0].replace("/", ".")

        component = cls._collect_component_from_py_module(
            component_path,
            working_dir=working_dir,
            force_reload=force_reload,
            component_name=component_name,
            from_executor=from_executor,
        )
        if not component and from_executor:
            raise NoComponentError(py_file, component_name)
        return component

    @classmethod
    def _collect_component_from_py_module(
        cls, py_module, working_dir, force_reload=False, component_name=None, from_executor=False
    ):
        """Collect single mldesigner component in a py module and return the executors of the components."""
        components = list(cls._collect_components_from_py_module(py_module, working_dir, force_reload))

        def defined_in_current_file(component):
            # The entry file here might not equal with inspect.getfile(component._func),
            # as we can define raw func in file A and wrap it with mldesigner component in file B.
            # For the example below, we got entry file as B here (the mldesigner component defined in).
            entry_file = component._entry_file
            component_path = py_module.replace(".", "/") + ".py"
            return Path(entry_file).resolve().absolute() == (Path(working_dir) / component_path).resolve().absolute()

        components = [
            component
            for component in components
            if defined_in_current_file(component) and (not component_name or component._name == component_name)
        ]
        if len(components) == 0:
            return None
        component = components[0]
        entry_file = Path(inspect.getfile(component._func))
        if len(components) > 1:
            if component_name and from_executor:
                raise TooManyComponentsError(len(components), entry_file, component_name)
            if component_name is None:
                # if component name not specified and there are more than one components, raise error
                raise RequiredComponentNameError(entry_file)

        return component

    @classmethod
    def _collect_components_from_py_module(cls, py_module, working_dir=None, force_reload=False):
        """Collect all components in a python module and return the executors of the components."""
        if isinstance(py_module, str):
            try:
                py_module = _import_component_with_working_dir(py_module, working_dir, force_reload)
            except Exception as e:
                msg = """Error occurs when import component '{}': {}.\n
                Please make sure all requirements inside conda.yaml has been installed."""
                raise ImportException(message=msg.format(py_module, e)) from e

        objects_with_source_line_order = sorted(
            inspect.getmembers(py_module, inspect.isfunction), key=lambda x: inspect.getsourcelines(x[1])[1]
        )

        for _, obj in objects_with_source_line_order:
            if cls._look_like_component(obj):
                EXECUTOR_CLASS = cls._get_executor_class(obj)
                component = EXECUTOR_CLASS(func=obj)
                component._check_py_module_valid(py_module)
                yield component

    @classmethod
    def _look_like_component(cls, f):
        """Return True if f looks like a component."""
        if not isinstance(f, types.FunctionType):
            return False
        if not hasattr(f, cls.INJECTED_FIELD):
            return False
        return True

    @classmethod
    def _get_executor_class(cls, func=None):
        # dynamic subgraph
        if func is not None and func._executor._type == ExecutorTypes.DYNAMIC:
            from mldesigner.dsl._dynamic_executor import DynamicExecutor

            return DynamicExecutor
        try:
            from mldesigner._dependent_component_executor import DependentComponentExecutor

            return DependentComponentExecutor
        except ImportException:
            return ComponentExecutor

    @abstractmethod
    def _refresh_instance(self, func: types.FunctionType):
        """Refresh current instance with new function."""

    def _check_py_module_valid(self, py_module):
        """Check whether the entry py module is valid to make sure it could be run in AzureML."""

    def _update_func(self, func: types.FunctionType):
        # Set the injected field so the function could be used to initializing with `ComponentExecutor(func)`
        setattr(func, self.INJECTED_FIELD, self._raw_entity_args)

    def _reload_func(self):
        """Reload the function to make sure the latest code is used to generate yaml."""
        f = self._func
        module = importlib.import_module(f.__module__)
        # if f.__name__ == '__main__', reload will throw an exception
        if f.__module__ != "__main__":
            from mldesigner._utils import _force_reload_module

            _force_reload_module(module)
        func = getattr(module, f.__name__)
        self._func = func._func if _is_mldesigner_component(func) else func
        self._refresh_instance(self._func)

    def execute(self, args: dict = None):
        """Execute the component with arguments."""
        execute_logger.info("Provided args: '%s'", args)
        args = self._parse(args)
        execute_logger.info("Parsed args: '%s'", self._trim_primitive_outputs_from_args(args))
        param_args, return_args = {}, {}
        # Split outputs specified by param and by return annotation
        for k, v in args.items():
            if k in self._return_mapping:
                return_args[k] = v
            else:
                param_args[k] = v

        # In case component function import other modules inside the function, need file directory in sys.path
        file_dir = str(Path(self._entry_file).parent)
        with inject_sys_path(file_dir):
            execute_logger.info("====================== User Logs ======================")
            res = self._func(**param_args)
            execute_logger.info("==================== User Logs End ====================")
            run_result_mapping = self._validate_execute_result_with_return_annotation(res)
            if return_args:
                self.finalize(run_result_mapping, return_args)

        return res

    def finalize(self, run_result_mapping, return_args):
        """Write file for outputs specified by return annotation, write RH for control outputs."""

        # prevent from returning same path to multiple asset outputs
        ASSET_PATH_SET = set()
        # Write outputs to file for outputs specified by return annotation
        execute_logger.debug("Finalizing outputs - writing primitive outputs to file, move non-primitive outputs:")
        for key, path in return_args.items():
            if key not in run_result_mapping:
                raise UserErrorException(f"Output with name {key!r} not found in run result {run_result_mapping}.")
            # skip early available output as it should have already been written when mark ready
            if self._return_mapping[key].early_available is True:
                continue

            if self._return_mapping[key].type in IoConstants.PRIMITIVE_STR_2_TYPE:
                # if return annotation is primitive type, write return value to file
                path = Path(path)
                if path.exists() and path.is_dir():
                    path = path / "output"  # refer to a file path if receive directory
                content = str(run_result_mapping[key])
                path.write_text(content)
                execute_logger.debug("\t[Write] '%s' -> '%s'", content, str(path.resolve().absolute()))
            elif self._return_mapping[key].type in self.SUPPORTED_RETURN_TYPES_ASSET:
                # if is uri_file or uri_folder, rename the user-created file/folder to return_args value
                dest_path = Path(path)
                res_path = Path(run_result_mapping[key])
                if dest_path.exists():
                    # if result path is the existing path itself, no need to do deleting-and-renaming
                    if dest_path == res_path:
                        continue
                    # pylint: disable=expression-not-assigned
                    os.remove(dest_path) if dest_path.is_file() else shutil.rmtree(dest_path)

                if res_path in ASSET_PATH_SET:
                    raise UserErrorException(
                        f"Identical path {res_path!r} is returned for multiple outputs in function "
                        f"{self._func.__name__!r}, please return different path to each uri_file/uri_folder output."
                    )
                ASSET_PATH_SET.add(res_path)

                # Tested several options other than shutil.move:
                # 1) os.link(): when running in remote, runtime give a mount point as destination path, os.link
                #    will raise cross-devices error since it's a different file system. Current component fails.
                # 2) os.symlink(): when running in remote, runtime will not collect the actual data and pass it
                #    to the next component. So current component succeeds while the next consuming component fails
                #    due to data access error.
                # 3) Both 1) and 2) options may cause error in local execution for asking admin permission.
                #
                # For efficiency test, 1 GB content(14 files with random string) took 7 seconds to get moved.
                shutil.move(res_path, dest_path)

                execute_logger.debug("\t[Move] '%s' -> '%s'", str(res_path), dest_path.resolve().absolute())

        # skip early available output as it has different field to write in RH
        primitive_output_keys = [
            key
            for key, output in self._return_mapping.items()
            if output._is_primitive_type and not output.early_available
        ]
        if primitive_output_keys:
            # write primitive outputs into run properties with mlflow
            # TODO(1955852): handle control outputs for mldesigner execute
            primitive_output_content = json.dumps(
                {k: v for k, v in run_result_mapping.items() if k in primitive_output_keys}
            )
            self.write_primitive_outputs_to_run_history(primitive_output_content=primitive_output_content)

    def _validate_execute_result_with_return_annotation(self, run_result):
        """Validate execution result with return annotation, convert run_result to mapping

        Validation rules:
            1. Primitive result is valid for primitive annotation:
                1) If run result is a integer, annotation must be "a()->int" or "a()->Output(type="integer")"
                2) A special valid case is, if run result is a string, except above two annotations, if can also be:
                     a. "a()->Output" because Output will be transforming to Output(type="uri_folder")
                     b. "a()->Output(type="uri_file/uri_folder")" because we return path for these two types

            2. Group result is valid for group annotation, and the group class must be the same:
                1) If run result is Group1(), annotation must be "a()->Group1"
                2) Every output inside group must pass primitive result check
                3) A special valid case is, if run result is Group1(), but annotation is "a()->Group2", and they
                    have the same output annotations.

            3. If return annotation is Output("uri_file/uri_folder"), check if the file/folder exists. It's supposed to
               be created inside user function.

        """
        supported_result_primitive_types = tuple(IoConstants.PRIMITIVE_TYPE_2_STR.keys())
        is_primitive_res = isinstance(run_result, supported_result_primitive_types)
        is_group_res = is_group(run_result)
        return_mapping_length = len(self._return_mapping)

        # check if return value is none when there is no return annotation
        if run_result is not None and return_mapping_length == 0:
            raise UserErrorException(f"No return annotation but got return value for function {self._func.__name__!r}")

        # check if run result is unsupported type, may remove if supporting custom type result
        if run_result and not is_primitive_res and not is_group_res:
            raise UserErrorException(
                f"Unsupported return type {type(run_result)!r} of function {self._func.__name__!r}, "
                f"only primitive type {supported_result_primitive_types} or @group decorated class are supported."
            )

        # check if returned None while function has return annotation
        if run_result is None and return_mapping_length != 0:
            raise UserErrorException(
                f"Returned result is None while function {self._func.__name__!r} "
                f"has return annotation: {self._return_mapping}."
            )

        # Check Rule No.1: Primitive result is valid for primitive annotation
        if is_primitive_res:
            if return_mapping_length > 1:
                raise UserErrorException(
                    f"Only 1 output was returned while multiple outputs are annotated "
                    f"for function {self._func.__name__!r}. Full annotations are: {self._return_mapping!r}"
                )

            annotation = list(self._return_mapping.values())[0]
            self._check_single_result_with_annotation(
                run_result=run_result,
                annotation=annotation,
            )

        # Check Rule No.2: Group result is valid for group annotation
        if is_group_res:
            res_dict = vars(run_result)
            annotations = self._return_mapping
            for name, annotation in annotations.items():
                self._check_single_result_with_annotation(
                    run_result=res_dict.get(name, None),
                    annotation=annotation,
                    name=name,
                )

        return self._get_run_result_mapping(run_result, is_primitive_res, is_group_res)

    def _check_single_result_with_annotation(self, run_result, annotation, name="output"):
        """Check a run result with its annotation"""
        if run_result is None:
            raise UserErrorException(f"Run result is None for output {name!r} of function {self._func.__name__!r}")

        does_match = False
        # pylint: disable=too-many-boolean-expressions
        if (
            # 1. Annotation is "a()->int/str/bool/float"
            (annotation in self.SUPPORTED_RETURN_TYPES_PRIMITIVE and isinstance(run_result, annotation))
            # 2. Annotation is "a()->Output(type="integer/string/boolean/number")"
            or (
                type(annotation).__name__ == "Output"
                and annotation.type == IoConstants.PRIMITIVE_TYPE_2_STR[type(run_result)]
            )
            or (
                isinstance(run_result, str)
                and (
                    # 3. Annotation is "a()->Output(type="uri_file/uri_folder")"
                    (type(annotation).__name__ == "Output" and annotation.type in self.SUPPORTED_RETURN_TYPES_ASSET)
                    # 4. Annotation is "a()->Output"
                    or (inspect.isclass(annotation) and annotation.__name__ == "Output")
                )
            )
        ):
            does_match = True

        if not does_match:
            expected_type = annotation
            if type(annotation).__name__ == "Output" and annotation.type in self.SUPPORTED_RETURN_TYPES_ASSET:
                expected_type = str
            elif inspect.isclass(annotation) and annotation.__name__ == "Output":
                expected_type = str
            elif not inspect.isclass(annotation) and type(annotation).__name__ == "Output":
                expected_type = IoConstants.PRIMITIVE_STR_2_TYPE[annotation.type]

            raise UserErrorException(
                f"Output with name {name!r} of function {self._func.__name__!r} does not match return annotation. "
                f"Got {type(run_result)!r} while expecting {expected_type!r}."
            )

        # Check Rule No.3 stated in _validate_execute_result_with_return_annotation():
        # Check if the returned file/folder exists
        if type(annotation).__name__ == "Output" and annotation.type in self.SUPPORTED_RETURN_TYPES_ASSET:
            if not Path(run_result).exists():
                raise UserErrorException(
                    f"Returned path {run_result!r} does not exist for function {self._func.__name__!r}, "
                    f"please double check if its created."
                )

    def _get_run_result_mapping(self, run_result, is_primitive_res, is_group_res):
        """Get run result mapping according to annotation"""
        run_result_mapping = {}
        if is_primitive_res:
            key = list(self._return_mapping.keys())[0]
            run_result_mapping[key] = run_result
        elif is_group_res:
            res_dict = vars(run_result)
            for name, value in res_dict.items():
                run_result_mapping[name] = value

        return run_result_mapping

    def _parse(self, args):
        """Validate args and parse with arg_mapping"""
        if isinstance(self._execution_args, dict):
            args = self._execution_args if not isinstance(args, dict) else {**self._execution_args, **args}

        refined_args = {}
        # validate parameter name, replace '-' with '_' when parameters come from command line
        for k, v in args.items():
            if not isinstance(k, str):
                raise UserErrorException(f"Execution args name must be string type, got {type(k)!r} instead.")
            new_key = k.replace("-", "_")
            if not new_key.isidentifier():
                raise UserErrorException(f"Execution args name {k!r} is not a valid python identifier.")
            refined_args[new_key] = v

        parsed_args = self._parse_with_mapping(refined_args, self._arg_mapping)
        global _parsed_args  # pylint: disable=global-statement
        _parsed_args = parsed_args.copy()
        return parsed_args

    @classmethod
    def _has_mldesigner_arg_mapping(cls, arg_mapping):
        for val in arg_mapping.values():
            if isinstance(val, (Input, Output)):
                return True
        return False

    def _parse_with_mapping(self, args, arg_mapping):
        """Use the parameters' info in arg_mapping to parse commandline params.

        :param args: A dict contains the actual param value for each parameter {'param-name': 'param-value'}
        :param arg_mapping: A dict contains the mapping from param key 'param_name' to _ComponentBaseParam
        :return: params: The parsed params used for calling the user function.

        Note: arg_mapping can be either azure.ai.ml.Input or mldesigner.Input, both will be handled here
        """
        # according to param definition, update actual arg or fill with default value
        self._refine_args_with_original_parameter_definition(args, arg_mapping)

        # If used with azure.ai.ml package,
        # all mldesigner Inputs/Outputs will be transformed to azure.ai.ml Inputs/Outputs
        # This flag helps to identify if arg_mapping is parsed with mldesigner io (standalone mode)
        has_mldesigner_io = self._has_mldesigner_arg_mapping(arg_mapping)
        # Convert the string values to real params of the function.
        params = {}
        params_with_no_value_provided = []
        for name, param in arg_mapping.items():
            type_name = type(param).__name__
            val = args.pop(name, None)
            # 1. If current param has no value
            if val is None:
                if self._is_unprovided_param(type_name=type_name, param=param):
                    params_with_no_value_provided.append(name)
                # If the Input is optional and no value set from args, set it as None for function to execute
                if type_name == "Input" and param.optional is True:
                    params[name] = None
                continue

            # 2. If current param has value:
            #       If it is a parameter, we help the user to parse the parameter, if it is an input port,
            #       we use load to get the param value of the port, otherwise we just pass the raw value.
            param_value = val

            # 2a. For Input params, parse primitive params to proper type, for other type Input, keep it as string
            if type_name == "Input" and param._is_primitive_type:
                try:
                    # Two situations are handled differently: mldesigner.Input and azure.ai.ml.Input
                    param_value = (
                        IoConstants.PARAM_PARSERS[param.type](val)
                        if has_mldesigner_io
                        else param._parse_and_validate(val)
                    )
                except Exception as e:
                    raise UserErrorException(
                        f"Parameter transition for {self._func.__name__!r} failed: For parameter {name!r}, " f"{e}"
                    )
            params[name] = param_value

            # 2b. For Output params, create dir for output path
            if type_name == "Output" and param.type == AssetTypes.URI_FOLDER and not Path(val).exists():
                Path(val).mkdir(parents=True, exist_ok=True)

        # For all required params that are not provided, collect them and raise exception
        if len(params_with_no_value_provided) > 0:
            raise UserErrorException(
                f"Required parameter values for {self._func.__name__!r} are not provided: "
                f"{params_with_no_value_provided!r}."
            )

        if self._is_variable_inputs:
            # TODO convert variable inputs to the corresponding type
            params.update(args)
        else:
            # used to notify user for additional args that are useless
            self._additional_args = args
        return params

    @classmethod
    def _is_unprovided_param(cls, type_name, param):
        # Note: here param value only contains user input except default value on function
        if type_name == "Output" or not param.optional:
            return True
        return False

    def _refine_args_with_original_parameter_definition(self, args, arg_mapping):
        """According to param definition, update actual arg or fill with default value.

        :param args: The actual args passed to execute component, need to be updated in this function.
        :type args: dict
        :param arg_mapping: Original parameters definition. Values are Input/Output objects.
        :type arg_mapping: dict

        Note: arg_mapping can be either azure.ai.ml.Input or mldesigner.Input, both will be handled here
        """

        for name, param in arg_mapping.items():
            type_name = type(param).__name__
            # work 1: Update args inputs with default value like "max_epocs=10".
            # Currently we only consider parameter as an optional parameter when user explicitly specified optional=True
            # in parameter's annotation like this: "max_epocs(type="integer", optional=True, default=10)". But we still
            # have to handle case like "max_epocs=10"
            if (
                # When used with main package, EnumInput needs to be handled
                type_name in ("Input", "EnumInput")
                and name not in args
                and param._is_primitive_type is True
                and param.default is not None
            ) or isinstance(param, _Param):
                args[name] = param.default

            # work 2: Update args outputs to ComponentName_timestamp/output_name
            if type_name == "Output":
                self._update_outputs_to_execution_args(args, param, name)

    @classmethod
    def _update_outputs_to_execution_args(cls, args, param, param_name):
        # if output is not specified, mldesigner will generate an output path automatically
        if param_name not in args:
            # if output path not specified, set as parameter name
            args[param_name] = param_name

    @classmethod
    def _get_output_annotations(cls, func, mapping: dict):
        """Analyze the annotation of the function to get the parameter mapping dict and the output port list.
        :param func:
        :return: (param_mapping, output_list)
            param_mapping: The mapping from function param names to input ports/component parameters;
            output_list: The output port list analyzed from return annotations.
        """
        # Outputs defined by return annotation will be added into mapping
        return_mapping = cls._get_outputs_from_return_annotation(func)

        for key, definition in return_mapping.items():
            if key in mapping:
                raise UserErrorException(
                    f"Duplicate output {key!r} found in both parameters "
                    f"and return annotations of function {func.__name__!r}."
                )
            mapping[key] = definition
        return return_mapping

    @classmethod
    def _get_standard_output_annotation(cls, annotation, func, output_name=None) -> dict:
        """Transform different returned types to standard Output"""
        exception_tail = (
            f"in return annotation of function {func.__name__!r}, expected instance types: "
            f"{list(cls.SUPPORTED_RETURN_TYPES_NON_PRIMITIVE) + cls.SUPPORTED_RETURN_TYPES_PRIMITIVE}) "
            f"with output types: {cls.SUPPORTED_TYPE_NAME_IN_OUTPUT_CLASS}."
            f'e.g. func()-> Output(type="{cls.SUPPORTED_TYPE_NAME_IN_OUTPUT_CLASS[0]}")'
        )
        # set output name as "output" if no output name specified
        output_name = cls.DEFAULT_OUTPUT_NAME if output_name is None else output_name

        if annotation is inspect.Parameter.empty:
            return {}

        # if annotation is the class, get a default instance
        if annotation in cls.SUPPORTED_RETURN_TYPES_NON_PRIMITIVE:
            annotation = annotation()

        # if annotation is _Param instance, transform to Output instance
        if isinstance(annotation, _Param):
            annotation = Output(**annotation._to_io_entity_args_dict())

        # if annotation is an instance of (Output, _Param)
        if isinstance(annotation, cls.SUPPORTED_RETURN_TYPES_NON_PRIMITIVE):
            # if annotation is Output but the type attribute string is not a known type string
            if annotation.type not in cls.SUPPORTED_TYPE_NAME_IN_OUTPUT_CLASS:
                raise UserErrorException(f"Unsupported output type {annotation.type!r} {exception_tail}")
            return {output_name: annotation}

        # if annotation is primitive type like str, return Output(type="string")
        if annotation in cls.SUPPORTED_RETURN_TYPES_PRIMITIVE:
            annotation = Output(type=IoConstants.PRIMITIVE_TYPE_2_STR[annotation])
            return {output_name: annotation}

        # if annotation is a Annotated[{primitive}, ...] type like Annotated[int, Field(min=1, max=10, default=0)]
        # Output is not support min, max, default
        if get_origin(annotation) is Annotated:
            hint_type, arg, *hint_args = get_args(annotation)  # pylint: disable=unused-variable
            if hint_type in cls.SUPPORTED_RETURN_TYPES_PRIMITIVE:
                if not isinstance(arg, cls.SUPPORTED_OUTPUT_METADATA):
                    raise UserErrorException(
                        f"Annotated Metadata class only support "
                        f"mldesigner._input_output.Meta, "
                        f"it is {type(arg)} now."
                    )
                if arg.type is not None and arg.type != hint_type:
                    raise UserErrorException(f"Meta class type value should be same as Annotated type: " f"{hint_type}")

                arg.type = hint_type
                annotation = Output(**arg._to_io_entity_args_dict())
                return {output_name: annotation}

        raise UserErrorException(f"Unsupported type {annotation!r} {exception_tail}")

    @classmethod
    def _get_outputs_from_return_annotation(cls, func):
        """Convert return annotation to Outputs.

        Supported type:
            1. dsl output type. func() -> Output(type='boolean') will be keep as they are.
            2. primitive output type, such as Output(type='string') will be converted to Output type.
            3. group type. func()->OutputClass will add output1 and output2 to component defined, with OutputClass:
                @group
                class OutputClass:
                    output1: bool
                    output2: Boolean()

        Note:
            - Single output without dataclass will be named as 'output'.
              If there are duplicate outputs, exception will be raised. i.e.
                func(output: Output)->Output  # Exception raised.
            - Nested dataclass object is not support.
        """

        return_annotation = inspect.signature(func).return_annotation

        if is_group(return_annotation):
            fields = getattr(return_annotation, IoConstants.GROUP_ATTR_NAME)
            fields_mapping = {}
            for name, annotation in fields.values.items():
                type_name = type(annotation).__name__
                if type_name == "GroupInput":
                    raise UserErrorException("Nested group return annotation is not supported.")
                # normalize annotation since currently annotation in @group will be converted to Input
                if type_name == "Input":
                    annotation = Output(type=annotation.type)
                fields_mapping.update(
                    cls._get_standard_output_annotation(annotation=annotation, func=func, output_name=name)
                )
            return fields_mapping

        return cls._get_standard_output_annotation(annotation=return_annotation, func=func)

    @classmethod
    def _update_environment(cls, environment_dict: dict, force_inject_deps: bool, has_control_output: bool):
        """Add mlflow dependency if control output exists. If failed to update, environment will be kept as it is."""
        if not isinstance(environment_dict, dict):
            if (
                isinstance(environment_dict, str)
                and environment_dict == CuratedEnv.MLDESIGNER_MINIMAL
                and has_control_output
            ):
                error_message = (
                    "The specified curated environment 'mldesigner-minimal' is not compatible with control output, "
                    "may replace it with curated environment 'mldesigner'."
                )
                raise UserErrorException(error_message)
            return environment_dict

        # copy env dict to avoid modifying the original one
        environment_dict = copy.deepcopy(environment_dict)
        mlflow_dependency = ["mlflow", "azureml-mlflow"]

        def has_dependency(dependency: str, dependencies_list: List[str]) -> bool:
            for _dep in dependencies_list:
                if _dep.startswith(dependency):
                    return True
            return False

        if not force_inject_deps and not has_control_output:
            return environment_dict
        try:
            deps = environment_dict["conda_file"]["dependencies"]
            for dep in deps:
                if isinstance(dep, dict) and "pip" in dep:
                    for mlflow_dep in mlflow_dependency:
                        if not has_dependency(mlflow_dep, dep["pip"]):
                            dep["pip"].append(mlflow_dep)
        except (AttributeError, KeyError):
            pass
        return environment_dict

    @classmethod
    def _write_control_outputs_to_run_history(cls, control_output_content: str):
        """Write control output content to run history."""
        return _write_properties_to_run_history(
            properties={cls.CONTROL_OUTPUTS_KEY: control_output_content},
            operation_name=RunHistoryOperations.WRITE_PRIMITIVE_OUTPUTS,
        )

    @classmethod
    def write_primitive_outputs_to_run_history(cls, primitive_output_content: str):
        """Write primitive output content to run history."""
        return cls._write_control_outputs_to_run_history(control_output_content=primitive_output_content)

    @classmethod
    def _require_deps_injection(cls, func) -> bool:
        for parameter in inspect.signature(func).parameters.values():
            annotation = parameter.annotation
            if getattr(annotation, "_is_primitive_type", None) or getattr(annotation, "early_available", None):
                return True
        return False

    def _trim_primitive_outputs_from_args(self, args):
        """Trim primitive outputs out from parsed args"""
        clean_args = {}
        for name, value in args.items():
            if name in self._arg_mapping:
                param = self._arg_mapping[name]
                if type(param).__name__ == "Output" and param.type in IoConstants.PRIMITIVE_STR_2_TYPE:
                    continue
            clean_args[name] = value
        return clean_args

    @classmethod
    def _refine_entity_args(cls, entity_args: dict, return_annotation: dict, force_inject_deps: bool) -> dict:
        # Deep copy because inner dict may be changed (environment or distribution).
        entity_args = copy.deepcopy(entity_args)
        tags = entity_args.get("tags", {})

        # Convert the type to support old style list tags.
        if isinstance(tags, list):
            tags = {tag: None for tag in tags}

        if not isinstance(tags, dict):
            raise ComponentDefiningError(name=entity_args["name"], cause="Keyword 'tags' must be a dict.")

        # Indicate the component is generated by mldesigner
        tags[ExecutorBase.CODE_GEN_BY_KEY] = ComponentSource.MLDESIGNER.lower()
        entity_args["tags"] = tags

        if "type" in entity_args and entity_args["type"] == "SweepComponent":
            return entity_args

        entity_args["distribution"] = entity_args.get("distribution", None)
        return entity_args

    @classmethod
    def _refine_environment(cls, environment, mldesigner_component_source_dir):
        return environment


class ComponentExecutor(ExecutorBase):
    """An executor to analyze the entity args of a function and convert it to a runnable component in AzureML."""

    def __init__(self, func: types.FunctionType, entity_args=None, _entry_file=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function wrapped by mldesigner.component.
        :type func: types.FunctionType
        """
        if isinstance(func, types.FunctionType):
            arg_mapping = self._standalone_analyze_annotations(func)
        else:
            arg_mapping = {}
        super().__init__(func=func, entity_args=entity_args, _entry_file=_entry_file, arg_mapping=arg_mapping)

    @classmethod
    def _standalone_analyze_annotations(cls, func):
        mapping = _standalone_get_param_with_standard_annotation(func)
        return mapping

    def _refresh_instance(self, func: types.FunctionType):
        self.__init__(self._func, entity_args=self._raw_entity_args, _entry_file=self._entry_file)
