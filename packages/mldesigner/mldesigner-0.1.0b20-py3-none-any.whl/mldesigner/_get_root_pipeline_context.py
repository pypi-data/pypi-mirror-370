# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import datetime
import json
import typing

from mldesigner._exceptions import SystemErrorException

STAGE_INIT = "Initialization"
STAGE_EXECUTION = "Execution"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


class PipelineStage:
    """Pipeline stage, valid stages are "Initialization" and "Execution".

    :param start_time: Stage start time, and you can get this in the string format of ISO 8601
        by calling `pipeline_stage.start_time.isoformat()`.
    :type start_time: datetime.datetime
    :param end_time: Stage end time, similar to start_time.
    :type end_time: datetime.datetime
    :param status: Stage status.
    :type status: str
    """

    def __init__(self, start_time: str, end_time: str, status: str):
        self.start_time = self._parse_time(start_time)
        self.end_time = self._parse_time(end_time)
        self.status = status

    @staticmethod
    def _parse_time(time_string: str) -> datetime.datetime:
        # %f for 6 digits, but backend may return different digit ms
        ms_start_index, ms_end_index = time_string.index("."), time_string.index("+")
        ms = time_string[ms_start_index + 1 : ms_end_index]
        normalized_ms = ms.ljust(6, "0")[:6]
        normalized_date_string = f"{time_string[:ms_start_index + 1]}{normalized_ms}{time_string[ms_end_index:]}"
        return datetime.datetime.strptime(normalized_date_string, TIME_FORMAT)

    @staticmethod
    def _from_stage(stage: typing.Optional[typing.Dict[str, str]]) -> typing.Optional["PipelineStage"]:
        if stage is None:
            return None
        return PipelineStage(stage["StartTime"], stage["EndTime"], stage["Status"])


class PipelineContext:
    """Pipeline context, including root pipeline job name and init and/or execution stage information.

    You can use `get_root_pipeline_context` to get this during pipeline runtime.

    :param root_job_name: Root pipeline job name.
    :type root_job_name: str
    :param initialization_stage: Initialization stage information.
    :type initialization_stage: PipelineStage
    :param execution_stage: Execution stage information.
    :type execution_stage: PipelineStage
    """

    def __init__(
        self,
        root_job_name: str,
        initialization_stage: typing.Optional[PipelineStage],
        execution_stage: typing.Optional[PipelineStage],
    ):
        self.root_job_name = root_job_name
        self.stages = {
            STAGE_INIT: initialization_stage,
            STAGE_EXECUTION: execution_stage,
        }

    @staticmethod
    def _from_job_properties(properties: typing.Dict) -> "PipelineContext":
        try:
            root_job_name = properties["rootRunId"]
            stages = json.loads(properties["properties"]["azureml.pipelines.stages"])
            init_stage = PipelineStage._from_stage(stages.get(STAGE_INIT))
            execution_stage = PipelineStage._from_stage(stages.get(STAGE_EXECUTION))
            return PipelineContext(root_job_name, init_stage, execution_stage)
        except (KeyError, json.decoder.JSONDecodeError, ValueError) as e:
            raise SystemErrorException("Parse pipeline job properties failed.") from e


def get_root_pipeline_context() -> PipelineContext:
    """Get root pipeline job information, including init/execution stage status and start/end time.
    Both init and execution stage are optional: for pipeline job without init job, init stage will be None;
    for pipeline job whose init job fails, execution stage will be None. This function will only work during runtime.

    .. code-block:: python

                from mldesigner import get_root_pipeline_context

                context = get_root_pipeline_context()
                root_job_name = context.root_job_name
                print("root pipeline job name:", root_job_name)
                # stage info, including statue, start/end time
                # note that init_stage and execution_stage can be None in some scenarios
                init_stage = context.stages["Initialization"]
                execution_stage = context.stages["Execution"]
                print("execution stage status:", execution_stage.status)
                print("execution stage start time:", execution_stage.start_time)
                print("execution stage end time:", execution_stage.end_time)

    """

    def _get_root_job_properties() -> typing.Dict:
        try:
            import mlflow
            from mlflow.tracking import MlflowClient
            from mlflow.utils.rest_utils import http_request
        except ImportError as e:
            error_message = "mlflow is required for `get_root_pipeline_context`, please install mlflow first."
            raise ImportError(error_message) from e

        def _get_job_properties(_cred, _experiment_id: str, _job_id: str) -> typing.Dict:
            return http_request(
                host_creds=_cred,
                endpoint="/experimentids/{}/runs/{}".format(_experiment_id, _job_id),
                method="GET",
            ).json()

        with mlflow.start_run() as run:
            client = MlflowClient()
            # get auth & update host to run history
            cred = client._tracking_client.store.get_host_creds()
            cred.host = (
                cred.host.replace("api.azureml.ms", "experiments.azureml.net")
                .replace("mlflow/v2.0", "mlflow/v1.0")
                .replace("mlflow/v1.0", "history/v1.0")
            )
            # get finalize job properties first to get root job id
            finalize_job_properties = _get_job_properties(cred, run.info.experiment_id, run.info.run_id)
            root_job_id = finalize_job_properties["rootRunId"]
            return _get_job_properties(cred, run.info.experiment_id, root_job_id)

    return PipelineContext._from_job_properties(_get_root_job_properties())
