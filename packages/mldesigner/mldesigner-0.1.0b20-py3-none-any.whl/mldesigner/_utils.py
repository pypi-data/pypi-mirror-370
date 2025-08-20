# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextlib
import copy
import functools
import importlib
import inspect
import logging
import os
import re
import sys
import types
from datetime import datetime
from enum import Enum as PyEnum
from pathlib import Path
from typing import IO, AnyStr, Dict, List, Optional, Tuple, Union

import pkg_resources
import pydash
import yaml

from mldesigner._constants import MLDESIGNER_COMPONENT_EXECUTION, VALID_NAME_CHARS, AssetTypes, IoConstants
from mldesigner._exceptions import ComponentException, UnexpectedKeywordError, UserErrorException, ValidationException
from mldesigner._logger_factory import _LoggerFactory


def is_valid_name(name: str):
    """Indicate whether the name is a valid component name."""
    return all(c in VALID_NAME_CHARS for c in name)


def _resolve_source_directory():
    """Resolve source directory as last customer frame's module file dir position."""
    source_file = _resolve_source_file()
    # Fall back to current working directory if not found
    return Path(os.getcwd()) if not source_file else Path(os.path.dirname(source_file)).absolute()


def _resolve_source_file():
    """Resolve source file as last customer frame's module file position."""
    try:
        frame_list = inspect.stack()
        # We find the last frame which is in SDK code instead of customer code or dependencies code
        # by checking whether the package name of the frame belongs to azure.ai.ml.component.
        pattern = r"(^mldesigner(?=\..*|$).*)"
        for frame, last_frame in zip(frame_list, frame_list[1:]):
            if _assert_frame_package_name(pattern, frame.frame) and not _assert_frame_package_name(
                pattern, last_frame.frame
            ):
                module = inspect.getmodule(last_frame.frame)
                return Path(module.__file__).absolute() if module else None
    # pylint: disable=broad-except
    except Exception:
        return None


def _assert_frame_package_name(pattern, frame):
    """Check the package name of frame is match pattern."""
    # f_globals records the function's module globals of the frame. And __package__ of module must be set.
    # https://docs.python.org/3/reference/import.html#__package__
    # Although __package__ is set when importing, it may happen __package__ does not exist in globals
    # when using exec to execute.
    package_name = frame.f_globals.get("__package__", "")
    return bool(package_name and re.match(pattern, package_name))


def _mldesigner_component_execution() -> bool:
    """Return True if mldesigner component is executing."""
    if os.getenv(MLDESIGNER_COMPONENT_EXECUTION, "false").lower() == "true":
        return True
    return False


def _relative_to(path, basedir, raises_if_impossible=False):
    """Compute the relative path under basedir.

    This is a wrapper function of Path.relative_to, by default Path.relative_to raises if path is not under basedir,
    In this function, it returns None if raises_if_impossible=False, otherwise raises.

    """
    # The second resolve is to resolve possible win short path.
    path = Path(path).resolve().absolute().resolve()
    basedir = Path(basedir).resolve().absolute().resolve()
    # if component code is set to be the file, basedir can be the same with path, return file name for this situation
    if basedir.is_file() and path == basedir:
        return Path(path.name)

    try:
        return path.relative_to(basedir)
    except ValueError:
        if raises_if_impossible:
            raise
        return None


def _is_mldesigner_component(function):
    return hasattr(function, "_is_mldesigner_component")


@contextlib.contextmanager
def _change_working_dir(path, mkdir=True):
    """Context manager for changing the current working directory"""

    saved_path = os.getcwd()
    if mkdir:
        os.makedirs(path, exist_ok=True)
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(saved_path)


def _import_component_with_working_dir(module_name, working_dir=None, force_reload=False):
    if working_dir is None:
        working_dir = os.getcwd()
    working_dir = str(Path(working_dir).resolve().absolute())

    with _change_working_dir(working_dir, mkdir=False), inject_sys_path(working_dir):
        try:
            py_module = importlib.import_module(module_name)
        except Exception as e:
            raise e
        except BaseException as e:
            # raise base exception like system.exit as normal exception
            raise ComponentException(message=str(e)) from e
        loaded_module_file = Path(py_module.__file__).resolve().absolute().as_posix()
        posix_working_dir = Path(working_dir).absolute().as_posix()
        if _relative_to(loaded_module_file, posix_working_dir) is None:
            if force_reload:
                # If force_reload is True, reload the module instead of raising exception.
                # This is used when we don't care the original module with the same name.
                return importlib.reload(py_module)
            raise RuntimeError(
                f"Could not import module: '{module_name}' because module with the same name has been loaded.\n"
                f"Path of the module: {loaded_module_file}\n"
                f"Working dir: {posix_working_dir}"
            )
        return py_module


@contextlib.contextmanager
def inject_sys_path(path):
    path_str = str(path)
    sys.path.insert(0, path_str)
    try:
        yield
    finally:
        if path_str in sys.path:
            sys.path.remove(path_str)


def _force_reload_module(module):
    # Reload the module except the case that module.__spec__ is None.
    # In the case module.__spec__ is None (E.g. module is __main__), reload will raise exception.
    if module.__spec__ is None:
        return module
    path = Path(module.__spec__.loader.path).parent
    with inject_sys_path(path):
        return importlib.reload(module)


@contextlib.contextmanager
def environment_variable_overwrite(key, val):
    if key in os.environ:
        backup_value = os.environ[key]
    else:
        backup_value = None
    os.environ[key] = val

    try:
        yield
    finally:
        if backup_value:
            os.environ[key] = backup_value
        else:
            os.environ.pop(key)


def _is_primitive_type(val):
    return val in (int, float, bool, str)


def _sanitize_python_class_name(snake_name: str):
    """Change variable name from snake to camel case."""
    components = snake_name.split("_")
    return "".join(component.title() for component in components)


class TimerContext(object):
    """A context manager calculates duration when executing inner block."""

    def __init__(self):
        self.start_time = None

    def get_duration_seconds(self):
        """Get the duration from context manger start to this function call.
        Result will be format to two decimal places.

        """
        duration = datetime.utcnow() - self.start_time
        return round(duration.total_seconds(), 2)

    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@contextlib.contextmanager
def update_logger_level(level):
    logger = logging.getLogger()
    backup_level = logger.level

    logger.setLevel(level)

    try:
        yield
    finally:
        logger.setLevel(backup_level)


def get_package_version(package_name):
    """Get the version of the package."""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None


def check_main_package(logger=None):
    if logger is None:
        logger = _LoggerFactory.get_logger("mldesigner")
    version = get_package_version("azure-ai-ml")
    target_version = "1.2.0"
    version_to_check = pkg_resources.parse_version(target_version)
    msg = (
        f"Mldesigner requires azure-ai-ml >= {target_version} package to be fully functional."
        f"It's highly recommended to install the latest azure-ai-ml package."
    )
    if version:
        if not version.startswith("0.0."):
            # public version
            if pkg_resources.parse_version(version) <= version_to_check:
                logger.warning(msg)
    else:
        logger.warning(msg)


def _is_mldesigner_component_function(func):
    return getattr(func, "_is_mldesigner_component", None) is True


def _is_dsl_pipeline_function(func):
    return getattr(func, "_is_dsl_func", None) is True


def _is_variable_args_function(func):
    is_variable_func = any(
        param.kind in [param.VAR_KEYWORD, param.VAR_POSITIONAL] for param in inspect.signature(func).parameters.values()
    )
    return is_variable_func


def _remove_empty_key_in_dict(data):
    if not isinstance(data, dict):
        return data
    res = {}
    for k, v in data.items():
        if v == {}:
            continue
        res[k] = _remove_empty_key_in_dict(v)
    return res


def get_credential_auth():
    """Get the available credential."""
    from azure.identity import (
        InteractiveBrowserCredential,
        ChainedTokenCredential,
        EnvironmentCredential,
        ManagedIdentityCredential,
        AzureCliCredential
    )

    try:
        credential =   ChainedTokenCredential(
            EnvironmentCredential(),
            ManagedIdentityCredential(),
            AzureCliCredential()
        )

        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception:  # pylint: disable=broad-except
        # Fall back to InteractiveBrowserCredential in case ChainedTokenCredential not work
        credential = InteractiveBrowserCredential()
    return credential


def _copy_func(f):
    """Copy func without deep copy as some method may contains fields can not be copied."""
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__  # cspell: ignore kwdefaults
    return g


def extract_input_output_name_from_binding(expression):
    """Use this func to process two format of output string and get valid output name:
    1: parent.jobs.a_job.output.a_port
    2: parent.inputs.a_input
    3: parent.outputs.b_output"""
    _jobs_regex = r"parent.jobs.([^.]+).([^.]+).([^.]+)\Z"
    _inputs_regex = r"parent.inputs.([^.]+)\Z"
    _outputs_regex = r"parent.outputs.([^.]+)\Z"

    if re.match(_jobs_regex, expression):
        expression_l = re.match(_jobs_regex, expression)
        return f"{expression_l.group(1)}.{expression_l.group(2)}.{expression_l.group(3)}"
    if re.match(_inputs_regex, expression):
        return re.match(_inputs_regex, expression).group(1)
    if re.match(_outputs_regex, expression):
        return re.match(_outputs_regex, expression).group(1)
    raise UserErrorException(f"Invalid input expression: {expression}")


def _normalize_identifier_name(name):
    normalized_name = name.lower()
    normalized_name = re.sub(r"[\W_]", " ", normalized_name)  # No non-word characters
    normalized_name = re.sub(" +", " ", normalized_name).strip()  # No double spaces, leading or trailing spaces
    if re.match(r"\d", normalized_name):
        normalized_name = "n" + normalized_name  # No leading digits
    return normalized_name


def _sanitize_python_variable_name(name: str):
    return _normalize_identifier_name(name).replace(" ", "_")


def get_all_data_binding_expressions(
    value: str, binding_prefix: Union[str, List[str]] = "", is_singular: bool = True
) -> List[str]:
    """Get all data-binding expressions in a value with specific binding
    target(prefix). Note that the function will return an empty list if the
    value is not a str.

    :param value: Value to extract.
    :param binding_prefix: Prefix to filter.
    :param is_singular: should the value be a singular data-binding expression, like "${{parent.jobs.xxx}}".
    :return: list of data-binding expressions.
    """
    if isinstance(binding_prefix, str):
        binding_prefix = [binding_prefix]
    if isinstance(value, str):
        target_regex = r"\$\{\{\s*(" + "\\.".join(binding_prefix) + r"\S*?)\s*\}\}"
        if is_singular:
            target_regex = "^" + target_regex + "$"
        return re.findall(target_regex, value)
    return []


class AMLVersionedArmId(object):
    """Parser for versioned arm id: e.g. /subscription/.../code/my-
    code/versions/1.

    :param arm_id: The versioned ARM id.
    :type arm_id: str
    :raises UserErrorException: Raised if the ARM id is incorrectly formatted.
    """

    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/(["
        "^/]+)/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(["
        "^/]+)"
    )
    PREFIX_REGEX_PATTERN = (
        "azureml:/subscriptions/([^/]+)/resource[gG]roups/([^/]+)/"  # cspell: ignore roups
        "providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(.+)"
    )

    def __init__(self, arm_id=None):
        self.is_registry_id = None
        if arm_id:
            match = re.match(AMLVersionedArmId.REGEX_PATTERN, arm_id) or re.match(
                AMLVersionedArmId.PREFIX_REGEX_PATTERN, arm_id
            )
            if match:
                self.subscription_id = match.group(1)
                self.resource_group_name = match.group(2)
                self.workspace_name = match.group(3)
                self.asset_type = match.group(4)
                self.asset_name = match.group(5)
                self.asset_version = match.group(6)
            else:
                REGISTRY_VERSION_PATTERN = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/versions/([^/]+)"
                match = re.match(REGISTRY_VERSION_PATTERN, arm_id)
                if match:
                    self.asset_name = match.group(3)
                    self.asset_version = match.group(4)
                    self.is_registry_id = True
                else:
                    raise UserErrorException(f"Invalid AzureML ARM versioned Id {arm_id}")


class AMLLabelledArmId(object):
    """Parser for versioned arm id: e.g. /subscription/.../code/my-
    code/labels/default.

    :param arm_id: The labelled ARM id.
    :type arm_id: str
    :raises UserErrorException: Raised if the ARM id is incorrectly formatted.
    """

    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/(["
        "^/]+)/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/labels/(["
        "^/]+)"
    )

    def __init__(self, arm_id=None):
        self.is_registry_id = None
        if arm_id:
            match = re.match(AMLLabelledArmId.REGEX_PATTERN, arm_id)
            if match:
                self.subscription_id = match.group(1)
                self.resource_group_name = match.group(2)
                self.workspace_name = match.group(3)
                self.asset_type = match.group(4)
                self.asset_name = match.group(5)
                self.asset_label = match.group(6)
            else:
                REGISTRY_VERSION_PATTERN = "^azureml://registries/([^/]+)/([^/]+)/([^/]+)/versions/([^/]+)"
                match = re.match(REGISTRY_VERSION_PATTERN, arm_id)
                if match:
                    self.asset_name = match.group(3)
                    self.asset_label = match.group(4)
                    self.is_registry_id = True
                else:
                    raise UserErrorException(f"Invalid AzureML ARM versioned Id {arm_id}")


def parse_name_version(name: str) -> Tuple[str, Optional[str]]:
    """Parser for Command.component in the format of "component_name:component_version"
    :param name: The Command.component
    :type name: str
    :raises UserErrorException: Raised if the name is incorrectly formatted
    :return parsed name and version
    """
    if name.find("/") != -1 and name[0] != "/":
        raise UserErrorException(f"Could not parse {name}. If providing an ARM id, it should start with a '/'.")
    token_list = name.split(":")
    if len(token_list) == 1:
        return name, None
    name, *version = token_list  # type: ignore
    return name, ":".join(version)


def _is_arm_id(component_str):
    try:
        AMLVersionedArmId(component_str)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def _is_name_version(component_str):
    try:
        parse_name_version(component_str)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def _is_name_label(component_str):
    try:
        AMLLabelledArmId(component_str)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def _is_instance_of(obj: object, cls_name):
    """Alternative of "isinstance(obj, cls)" without actually importing the class"""
    if isinstance(cls_name, str):
        return any(cls_name == cls.__name__ for cls in type(obj).__mro__)
    if isinstance(cls_name, tuple):
        for item in cls_name:
            for cls in type(obj).__mro__:
                if item == cls.__name__:
                    return True
        return False

    raise UserErrorException(f"The second argument must be a string or a tuple, got {type(cls_name)!r}.")


def _assert_arg_valid(io_names: dict, keys: list, func_name: str):
    """Assert the arg keys are all in keys."""
    # pylint: disable=protected-access
    # validate component input names
    try:
        from mldesigner._azure_ai_ml import Component
    except ImportError:
        raise UserErrorException("Please install azure-ai-ml package.")

    Component._validate_io_names(io_names=io_names, raise_error=True)

    lower2original_parameter_names = {x.lower(): x for x in keys}
    kwargs_need_to_update = []
    for key in io_names:
        if key not in keys:
            lower_key = key.lower()
            if lower_key in lower2original_parameter_names:
                # record key that need to update
                kwargs_need_to_update.append(key)
            else:
                raise UnexpectedKeywordError(func_name=func_name, keyword=key, keywords=keys)
    # update kwargs to align with yaml definition
    for key in kwargs_need_to_update:
        io_names[lower2original_parameter_names[key.lower()]] = io_names.pop(key)


def private_features_enabled():
    return os.getenv("AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED") in ["True", "true", True]


def is_group(obj):
    """Return True if obj is a group or an instance of a parameter group class."""
    return hasattr(obj, IoConstants.GROUP_ATTR_NAME)


def _write_properties_to_run_history(properties: dict, operation_name: str) -> None:
    """Write properties dict to run history."""
    logger = _LoggerFactory.get_logger("mldesigner")
    logger.info("Start writing properties '%s' to run history...", properties)

    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        from mlflow.utils.rest_utils import http_request

    except ImportError as e:
        raise ImportError(f"mlflow is required to {operation_name}. Please install mlflow first.") from e

    # get mlflow run
    run = mlflow.active_run()
    if run is None:
        run = mlflow.start_run()
    logger.info("Got run '%s' in experiment '%s'", run.info.run_id, run.info.experiment_id)
    # get auth from client
    client = MlflowClient()
    try:
        cred = client._tracking_client.store.get_host_creds()  # pylint: disable=protected-access
        # update host to run history and request PATCH API
        cred.host = cred.host.replace("mlflow/v2.0", "mlflow/v1.0").replace("mlflow/v1.0", "history/v1.0")
        response = http_request(
            host_creds=cred,
            endpoint=f"/experimentids/{run.info.experiment_id}/runs/{run.info.run_id}",
            method="PATCH",
            json={"runId": run.info.run_id, "properties": properties},
        )
        if response.status_code == 200:
            logger.info("Finish writing properties '%s' to run history", properties)
        else:
            logger.error("Fail writing properties '%s' to run history: %s", properties, response.text)
            response.raise_for_status()
    except AttributeError as e:
        logger.error("Fail writing properties '%s' to run history: %s", properties, e)


def _get_annotation_cls_by_type(t: type, raise_error=False, optional=None, is_dependency=False):
    if is_dependency:
        from mldesigner._azure_ai_ml import Input
    else:
        from mldesigner._input_output import Input

    cls = Input._get_input_by_type(t=t, optional=optional)  # pylint: disable=protected-access
    if cls is None and raise_error:
        raise UserErrorException(f"Can't convert type {t} to mldesigner.Input")
    return cls


def _get_annotation_by_value(val, is_dependency=False):
    if is_dependency:
        from mldesigner._azure_ai_ml import Input
    else:
        from mldesigner._input_output import Input, String

    if val is inspect.Parameter.empty or val is None:
        # If no default value or default is None, create val as the basic parameter type,
        # it could be replaced using component parameter definition.
        annotation = Input._get_default_unknown_input()  # pylint: disable=protected-access
    elif isinstance(val, PyEnum):
        # Handle enum values
        if is_dependency:
            enum = String._assert_enum_valid(val.__class__)  # pylint: disable=protected-access
            annotation = Input(type="string", enum=enum)
        else:
            annotation = String(enum=val.__class__)
    else:
        # for types generated from default value, regard it as optional input
        annotation = _get_annotation_cls_by_type(type(val), raise_error=False, is_dependency=is_dependency)
        if not annotation:
            # Fall back to default
            annotation = Input._get_default_unknown_input()  # pylint: disable=protected-access
    return annotation


def get_auth():
    from azure.identity import AzureCliCredential, ClientSecretCredential

    auth = AzureCliCredential()

    tenant_id = os.getenv("tenantId", None)
    sp_id = os.getenv("servicePrincipalId", None)
    sp_secret = os.getenv("servicePrincipalKey", None)

    if tenant_id and sp_id and sp_secret:
        auth = ClientSecretCredential(tenant_id, sp_id, sp_secret)
        print(f"Using Service Principal auth with tenantId {tenant_id}")

    return auth


def load_yaml(source: Optional[Union[AnyStr, os.PathLike, IO]]) -> Dict:
    # null check - just return an empty dict.
    # Certain CLI commands rely on this behavior to produce a resource
    # via CLI, which is then populated through CLArgs.
    """Load a local YAML file.
    :param source: The relative or absolute path to the local file.
    :type source: str
    :raises ~mldesigner._exceptions.ValidationException: Raised if file or folder cannot be successfully loaded.
        Details will be provided in the error message.
    :return: A dictionary representation of the local file's contents.
    :rtype: Dict
    """
    if source is None:
        return {}
    # pylint: disable=redefined-builtin
    input = None  # type: IOBase
    must_open_file = False
    try:  # check source type by duck-typing it as an IOBase
        readable = source.readable()
        if not readable:  # source is misformatted stream or file
            msg = "File Permissions Error: The already-open \n\n inputted file is not readable."
            raise ValidationException(
                message=msg,
            )
        # source is an already-open stream or file, we can read() from it directly.
        input = source
    except AttributeError:
        # source has no writable() function, assume it's a string or file path.
        must_open_file = True
    if must_open_file:  # If supplied a file path, open it.
        try:
            input = open(source, "r", encoding="utf-8")
        except OSError:  # FileNotFoundError introduced in Python 3
            raise ValidationException(
                message=f"No such file or directory: {source}",
            )
    # input should now be an readable file or stream. Parse it.
    cfg = {}
    try:
        cfg = yaml.safe_load(input)
    except yaml.YAMLError as e:
        msg = f"Error while parsing yaml file: {source} \n\n {str(e)}"
        raise ValidationException(
            message=msg,
        )
    finally:
        if must_open_file:
            input.close()
    return cfg


def _get_io_name(io: object):
    """
    A compatible method to get io name of azure-ai-ml Input/Output.

    Starting from azure-ai-ml=1.5.0, original attribute "name" is used to represent the registered data name,
    we use "_port_name" instead in internal code logic.
    """
    new_io_name = "_port_name"
    # package version: azure-ai-ml > 1.4.0
    if hasattr(io, new_io_name):
        return getattr(io, new_io_name)
    # package version: azure-ai-ml <= 1.4.0
    return io.name


def _get_node_io_name(io: object):
    """
    A compatible method to get io name of azure-ai-ml NodeInput/NodeOutput/PipelineInput/PipelineOutput.

    Starting from azure-ai-ml=1.5.0, we use "_port_name" in internal code logic.
    """
    new_io_name = "_port_name"
    # package version: azure-ai-ml > 1.4.0
    if hasattr(io, new_io_name):
        return getattr(io, new_io_name)
    # package version: azure-ai-ml <= 1.4.0
    return io._name  # pylint: disable=protected-access


def _get_all_enum_values_iter(enum_type):
    """Get all values of an enum type."""
    for key in dir(enum_type):
        if not key.startswith("_"):
            yield getattr(enum_type, key)


def _convert_internal_type(param_type):
    # Convert internal output type to v2 output type
    if param_type in list(_get_all_enum_values_iter(AssetTypes)):
        pass
    elif param_type in ["AnyFile"]:
        param_type = AssetTypes.URI_FILE
    else:
        # Handle AnyDirectory and the other types.
        param_type = AssetTypes.URI_FOLDER
    return param_type


def _detect_output_types(output_cls):
    """Get output types from the output class comments generated by generate_package."""
    regex = r"(\S*): .*\n[ ].*\"\"\".*\(type: (\S.*)\)\"\"\""
    source_code = inspect.getsource(output_cls)
    output_types = re.findall(regex, source_code)
    return output_types


def omit_single_with_wildcard(obj, omit_field: str):
    """
    Support .*. for pydash.omit
        omit_with_wildcard({"a": {"1": {"b": "v"}, "2": {"b": "v"}}}, "a.*.b")
        {"a": {"1": {}, "2": {}}}
    """
    obj = copy.deepcopy(obj)
    target_mark = ".*."
    if target_mark in omit_field:  # pylint: disable=no-else-return
        prefix, next_omit_field = omit_field.split(target_mark, 1)
        new_obj = pydash.get(obj, prefix)
        if new_obj:
            for key, value in new_obj.items():
                new_obj[key] = omit_single_with_wildcard(value, next_omit_field)
            pydash.set_(obj, prefix, new_obj)
        return obj
    else:
        return pydash.omit(obj, omit_field)


def omit_with_wildcard(obj, *properties: str):
    for omit_field in properties:
        obj = omit_single_with_wildcard(obj, omit_field)
    return obj


def is_internal_component(component):
    """Check if the component is internal component.

    Use class name to check to avoid import InternalComponent in mldesigner.
    """
    # azure-ai-ml package is an optional dependency, so use local import.
    from ._azure_ai_ml import Component

    if not isinstance(component, Component):
        return False
    if re.match(r"Internal.*Component", component.__class__.__name__):
        return True
    return False
