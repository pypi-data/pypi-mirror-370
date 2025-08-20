# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
from pathlib import Path

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import ManagedIdentityCredential, InteractiveBrowserCredential
from mldesigner._component_executor import execute_logger
from mldesigner._constants import (
    IMPORT_AZURE_AI_ML_ERROR_MSG,
    USE_CURATED_ENV_AS_DEFAULT,
    AssetTypes,
    CuratedEnv,
    CustomizedEnvMldesigner,
    ExecutorTypes,
    IdentityEnvironmentVariable,
    RunHistoryOperations,
    SupportedParameterTypes,
)
from mldesigner._dependent_component_executor import DependentComponentExecutor
from mldesigner._exceptions import ImportException, SystemErrorException, UserErrorException
from mldesigner._utils import _write_properties_to_run_history, inject_sys_path

try:
    from mldesigner._azure_ai_ml import (
        AzureMLOnBehalfOfCredential,
        Environment,
        MLClient,
        PipelineComponent,
        PipelineJob,
        get_ignore_file,
        pipeline,
    )

except ImportError:
    raise ImportException(IMPORT_AZURE_AI_ML_ERROR_MSG)

asset_types = AssetTypes()
_DATA_PATH = Path(__file__).resolve().parent.parent / "data"
_DEFAULT_IGNORE_FILE = _DATA_PATH / "dynamic_default_ignore_file"


class DynamicExecutor(DependentComponentExecutor):
    """Currently dynamic executor will only work in compile time."""

    PIPELINE_COMPONENT_KEY = "azureml.pipelines.subPipelineComponent"
    PIPELINE_COMPONENT_ID_KEY = "azureml.pipelines.dynamicSubPipelineComponentId"
    DYNAMIC_COMPONENT_PROPERTY_KEY = "azureml.pipelines.dynamic"
    SUPPORTED_RETURN_TYPES_ASSET = [getattr(asset_types, k) for k in dir(asset_types) if k.isupper()]
    SUPPORTED_TYPE_NAME_IN_OUTPUT_CLASS = list(SupportedParameterTypes) + SUPPORTED_RETURN_TYPES_ASSET
    IGNORE_FILE_NAME = ".amlignore"

    def __init__(self, **kwargs):
        """Initialize a DynamicExecutor with a function to enable calling the function with command line args."""
        super(DynamicExecutor, self).__init__(**kwargs)

        # Add dynamic hint to properties
        properties = self._entity_args.get("properties", {})
        properties[self.DYNAMIC_COMPONENT_PROPERTY_KEY] = "true"
        self._entity_args["properties"] = properties
        self._type = ExecutorTypes.DYNAMIC
        # store pipeline component meta in executor for debug
        self._execution_result = {}
        # store actual pipeline component created in runtime
        self._pipeline_component = None

    @classmethod
    def _update_outputs_to_args(cls, args, outputs):
        # won't add outputs to command args for dynamic executor
        pass

    def _update_outputs_to_execution_args(self, args, param, param_name):
        # won't add outputs to execution args for dynamic executor
        pass

    @classmethod
    def _is_unprovided_param(cls, type_name, param):
        # Note: unprovided outputs won't raise exception
        if type_name == "Input" and not param.optional:
            return True
        return False

    @classmethod
    def _create_default_ignore_file(cls):
        """Create a default ignore file in current working directory to ignore runtime attached user_logs folder."""
        target_file = Path("./") / cls.IGNORE_FILE_NAME
        ignore_file = get_ignore_file(directory_path="./")
        if ignore_file.exists():
            # won't create default ignore file if user already has one because it may shadow user's .gitignore file
            execute_logger.info("Ignore file %s exists, skip creating default ignore file.", ignore_file)
        else:
            execute_logger.info("Creating default ignore file: %s", target_file)
            with open(_DEFAULT_IGNORE_FILE) as f:
                file_content = f.read()
            with open(target_file, "w") as f:
                f.write(file_content)

    def prepare(self):
        """Pre-process for execution."""
        self._create_default_ignore_file()

    def execute(self, args: dict = None):
        """Execute the dynamic component with arguments."""
        # pylint: disable=protected-access,
        self.prepare()
        self._execution_result = {}
        original_func = self._func

        execute_logger.info("Provided args: '%s'", args)
        args = self._parse(args)
        execute_logger.info("Parsed args: '%s'", args)
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
            # "compile" dynamic pipeline to pipeline job
            pipeline_job = pipeline(original_func)(**args)
            execute_logger.info("==================== User Logs End ====================")

        if not isinstance(pipeline_job, PipelineJob):
            raise SystemErrorException(
                f"Expecting compiled dynamic subgraph to be a PipelineJob, got {type(pipeline_job)} instead."
            )

        # 1. extract pipeline component.
        pipeline_component = pipeline_job.component
        self._pipeline_component = pipeline_component

        # 2. validate pipeline component.
        try:
            pipeline_component_dict = pipeline_component._to_dict()
        except Exception as e:  # pylint: disable=broad-except
            execute_logger.error("Failed to serialize pipeline component: %s", e)
            pipeline_component_dict = {}

        # return the generated pipeline component dict and log in stream outputs for debugging
        self._execution_result[self.PIPELINE_COMPONENT_KEY] = pipeline_component_dict
        execute_logger.info("Generated pipeline component: %s", json.dumps(pipeline_component_dict))
        pipeline_component_inputs = pipeline_component_dict.get("inputs")
        pipeline_component_outputs = pipeline_component_dict.get("outputs")

        try:
            command_component_dict = self.component._to_dict()
        except Exception as e:  # pylint: disable=broad-except
            execute_logger.error("Failed to serialize command component: %s", e)
            command_component_dict = {}

        command_component_inputs = command_component_dict.get("inputs")
        command_component_outputs = command_component_dict.get("outputs")

        # warning if created pipeline component has different interface as command component
        error_message = (
            "Generated pipeline component has different {name} with original dynamic component. "
            "Pipeline component {name}: {field}, dynamic subgraph {name}: {field2}"
        )

        if pipeline_component_inputs != command_component_inputs:
            # pylint: disable=logging-format-interpolation
            execute_logger.warning(
                error_message.format(name="inputs", field=pipeline_component_inputs, field2=command_component_inputs)
            )
        if pipeline_component_outputs != command_component_outputs:
            # pylint: disable=logging-format-interpolation
            execute_logger.warning(
                error_message.format(name="outputs", field=pipeline_component_outputs, field2=command_component_outputs)
            )
            self._validate_pipeline_component_outputs(
                pipeline_component=pipeline_component,
                pipeline_outputs=pipeline_component_outputs,
                command_outputs=command_component_outputs,
            )

        # 3. create pipeline component if is online run.
        if self._is_online_run():
            pipeline_component = self._create_pipeline_component(pipeline_component)
            # add created pipeline component id to execution result for debug
            self._execution_result[self.PIPELINE_COMPONENT_ID_KEY] = pipeline_component.id
            execute_logger.info("Created pipeline component: %s", pipeline_component.id)

        execute_logger.info("==================== System Logs End ====================")
        # executor won't write anything to command outputs
        # DCM will make sure inner pipeline jobs output bind to this command outputs

        return {}

    def _create_pipeline_component(self, pipeline_component: PipelineComponent) -> PipelineComponent:
        """Create pipeline component using obo token, return created pipeline component."""
        # pylint: disable=protected-access, broad-except
        execute_logger.info("Creating pipeline component")

        # step1: connect client with obo token
        ml_client = self._get_ml_client()

        # step2: create anonymous pipeline component
        pipeline_component = ml_client.components.create_or_update(pipeline_component, is_anonymous=True)
        execute_logger.info("Finished create pipeline component: %s", pipeline_component.id)
        try:
            execute_logger.info("Spec: %s", json.dumps(pipeline_component._to_dict()))
        except Exception:
            pass

        # step3: write component id to run history
        _write_properties_to_run_history(
            properties={self.PIPELINE_COMPONENT_ID_KEY: pipeline_component.id},
            operation_name=RunHistoryOperations.WRITE_COMPONENT_ID,
        )

        return pipeline_component

    @classmethod
    def _is_online_run(cls):
        """Check if the run is online."""
        # TODO: find a better way
        return os.getenv("AZUREML_RUN_ID") is not None

    @classmethod
    def _get_ml_client(cls):
        # May return a different one if executing in local

        # credential priority: OBO > managed identity > default
        # check OBO via environment variable, the referenced code can be found from below search:
        # https://msdata.visualstudio.com/Vienna/_search?text=AZUREML_OBO_ENABLED&type=code&pageSize=25&filters=ProjectFilters%7BVienna%7D&action=contents
        if os.getenv(IdentityEnvironmentVariable.OBO_ENABLED_FLAG):
            print("User identity is configured, use OBO credential.")
            credential = AzureMLOnBehalfOfCredential()
        else:
            client_id_from_env = os.getenv(IdentityEnvironmentVariable.DEFAULT_IDENTITY_CLIENT_ID)
            if client_id_from_env:
                # use managed identity when client id is available from environment variable.
                # reference code:
                # https://learn.microsoft.com/en-us/azure/machine-learning/how-to-identity-based-service-authentication?tabs=cli#compute-cluster
                print("Use managed identity credential.")
                credential = ManagedIdentityCredential(client_id=client_id_from_env)
            else:
                # use interactive browser credential to handle other cases.
                print("Use Interactive browser credential.")
                credential = InteractiveBrowserCredential()
        # finally try to get access token to validate credential
        try:
            credential.get_token("https://management.azure.com/")
        except ClientAuthenticationError as e:
            error_message = (
                "Failed to retrieve token with current credential, please configure proper identity and retry. "
                "For example, you can set user identity for this dynamic node with code: "
                "`<dynamic-node>.identity = UserIdentityConfiguration()`, "
                "which will create dynamic pipeline component on behalf of you, and it works in most cases."
            )
            raise UserErrorException(error_message) from e

        # TODO: allow user set debug mode
        return MLClient(
            workspace_name=os.getenv("AZUREML_ARM_WORKSPACE_NAME"),
            subscription_id=os.getenv("AZUREML_ARM_SUBSCRIPTION"),
            resource_group_name=os.getenv("AZUREML_ARM_RESOURCEGROUP"),
            credential=credential,
        )

    @classmethod
    def _get_default_env(cls, has_control_output: bool = False):
        """Return default environment."""
        # for dynamic environment, `has_control_output` is meaningless as mldesigner is always picked here.
        if USE_CURATED_ENV_AS_DEFAULT:
            return CuratedEnv.MLDESIGNER
        return Environment(image=CustomizedEnvMldesigner.IMAGE, conda_file=CustomizedEnvMldesigner.CONDA_FILE)

    @classmethod
    def _validate_pipeline_component_outputs(cls, pipeline_component, pipeline_outputs, command_outputs):
        """Validate if pipeline component output matches the command component wrapper.
        If only description unmatch, use description in annotation overwrite actual output annotation.
        Otherwise, raise error.
        """
        # pylint: disable=logging-fstring-interpolation, protected-access

        error_prefix = "Unmatched outputs between actual pipeline output and output in annotation"
        if pipeline_outputs.keys() != command_outputs.keys():
            raise UserErrorException(
                "{}: actual pipeline component outputs: {}, annotation outputs: {}".format(
                    error_prefix, pipeline_outputs.keys(), command_outputs.keys()
                )
            )

        unmatched_outputs = []
        for key, actual_output in pipeline_outputs.items():
            expected_output = command_outputs[key]
            actual_output.pop("description", None)
            expected_description = expected_output.pop("description", None)
            if expected_output != actual_output:
                unmatched_outputs.append(
                    f"{key}: pipeline component output: {actual_output} != annotation output {expected_output}"
                )
            if expected_description:
                execute_logger.debug(
                    f"Updating output {key!r}'s description to {expected_description!r} according to annotation."
                )
                pipeline_component.outputs[key]._description = expected_description

        if unmatched_outputs:
            raise UserErrorException(f"{error_prefix}: {unmatched_outputs}")
