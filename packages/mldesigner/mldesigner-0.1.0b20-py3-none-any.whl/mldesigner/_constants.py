# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

BASE_PATH_CONTEXT_KEY = "base_path"
VALID_NAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-")
MLDESIGNER_COMPONENT_EXECUTION = "MLDESIGNER_COMPONENT_EXECUTION"
MLDESIGNER_COMPONENT_EXECUTOR_MODULE = "mldesigner.executor"
IMPORT_AZURE_AI_ML_ERROR_MSG = (
    "Dependent component executor can not be used in standalone mode. Please install azure.ai.ml package."
)
REGISTRY_URI_FORMAT = "azureml://registries/"
MLDESIGNER_IMPORTS_MODULE = "azure.ai.ml.dsl._mldesigner"
ARM_ID_PREFIX = "azureml:"
# normally use curated env as default env, when the flag is set to false, we can specify runtime default env and
# this is convenient for dev work
USE_CURATED_ENV_AS_DEFAULT = True
AML_IGNORE_SUFFIX = ".amlignore"
GIT_IGNORE_SUFFIX = ".gitignore"


class NodeType(object):
    COMMAND = "command"
    SWEEP = "sweep"
    PARALLEL = "parallel"
    AUTOML = "automl"
    PIPELINE = "pipeline"
    IMPORT = "import"
    SPARK = "spark"
    DATA_TRANSFER = "data_transfer"
    FLOW_PARALLEL = "promptflow_parallel"
    # Note: container is not a real component type,
    # only used to mark component from container data.
    _CONTAINER = "_container"


class InternalNodeType:
    COMMAND = "CommandComponent"
    DATA_TRANSFER = "DataTransferComponent"
    DISTRIBUTED = "DistributedComponent"
    HDI = "HDInsightComponent"
    PARALLEL = "ParallelComponent"
    SCOPE = "ScopeComponent"
    STARLITE = "StarliteComponent"
    SWEEP = "SweepComponent"
    PIPELINE = "PipelineComponent"
    HEMERA = "HemeraComponent"
    AE365EXEPOOL = "AE365ExePoolComponent"
    IPP = "IntellectualPropertyProtectedComponent"
    SPARK = "spark"

    @classmethod
    def all_values(cls):
        all_values = []
        for key, value in vars(cls).items():
            if not key.startswith("_") and isinstance(value, str):
                all_values.append(value)
        return all_values


class CuratedEnv:
    MLDESIGNER = "azureml://registries/azureml/environments/mldesigner/labels/latest"
    MLDESIGNER_MINIMAL = "azureml://registries/azureml/environments/mldesigner-minimal/labels/latest"


class CustomizedEnvMldesignerMinimal:
    CONDA_FILE = {
        "name": "default_environment",
        "channels": ["defaults"],
        "dependencies": [
            "python=3.8.12",
            "pip=21.2.2",
            {
                "pip": [
                    "mldesigner",
                ]
            },
        ],
    }
    IMAGE = "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"


class CustomizedEnvMldesigner(CustomizedEnvMldesignerMinimal):
    CONDA_FILE = {
        "name": "default_environment",
        "channels": ["defaults"],
        "dependencies": [
            "python=3.8.12",
            "pip=21.2.2",
            {
                "pip": [
                    "mldesigner",
                    "azure-ai-ml",
                    "mlflow",
                    "azureml-mlflow",
                ]
            },
        ],
    }


class ComponentSource:
    """Indicate where the component is constructed."""

    MLDESIGNER = "MLDESIGNER"
    BUILDER = "BUILDER"
    DSL = "DSL"
    CLASS = "CLASS"
    REMOTE_WORKSPACE_JOB = "REMOTE.WORKSPACE.JOB"
    REMOTE_WORKSPACE_COMPONENT = "REMOTE.WORKSPACE.COMPONENT"
    REMOTE_REGISTRY = "REMOTE.REGISTRY"
    YAML_JOB = "YAML.JOB"
    YAML_COMPONENT = "YAML.COMPONENT"


class IoConstants:
    PRIMITIVE_STR_2_TYPE = {"integer": int, "string": str, "number": float, "boolean": bool}
    PRIMITIVE_TYPE_2_STR = {int: "integer", str: "string", float: "number", bool: "boolean"}
    TYPE_MAPPING_YAML_2_REST = {
        "string": "String",
        "integer": "Integer",
        "number": "Number",
        "boolean": "Boolean",
    }
    PARAM_PARSERS = {
        "float": float,
        "integer": lambda v: int(float(v)),  # backend returns 10.0 for integer, parse it to float before int
        "boolean": lambda v: str(v).lower() == "true",
        "number": float,
        "string": str,
    }
    # For validation, indicates specific parameters combination for each type
    INPUT_TYPE_COMBINATION = {
        "uri_folder": ["path", "mode"],
        "uri_file": ["path", "mode"],
        "mltable": ["path", "mode"],
        "mlflow_model": ["path", "mode"],
        "custom_model": ["path", "mode"],
        "integer": ["default", "min", "max"],
        "number": ["default", "min", "max"],
        "string": ["default"],
        "boolean": ["default"],
    }
    GROUP_ATTR_NAME = "__dsl_group__"
    GROUP_TYPE_NAME = "group"


class AssetTypes:
    URI_FILE = "uri_file"
    URI_FOLDER = "uri_folder"
    MLTABLE = "mltable"
    MLFLOW_MODEL = "mlflow_model"
    TRITON_MODEL = "triton_model"
    CUSTOM_MODEL = "custom_model"


class ErrorCategory:
    USER_ERROR = "UserError"
    SYSTEM_ERROR = "SystemError"
    UNKNOWN = "Unknown"


class SupportedParameterTypes(str, Enum):  # pylint: disable=enum-must-inherit-case-insensitive-enum-meta
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"


class ExecutorTypes:
    DYNAMIC = "dynamic"


class RunHistoryOperations:
    MARK_OUTPUT_READY = "mark output ready"
    WRITE_COMPONENT_ID = "write component id"
    WRITE_PRIMITIVE_OUTPUTS = "write primitive outputs"


class IdentityEnvironmentVariable:
    DEFAULT_IDENTITY_CLIENT_ID = "DEFAULT_IDENTITY_CLIENT_ID"
    OBO_ENABLED_FLAG = "AZUREML_OBO_ENABLED"
