# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Union

from mldesigner._exceptions import UserErrorException
from mldesigner._logger_factory import _LoggerFactory
from mldesigner._utils import private_features_enabled

compare_logger = _LoggerFactory.get_logger("compare")
az_ml_logger = _LoggerFactory.get_logger("az-ml")


def compare(
    job_url1: str,
    job_url2: str,
    target_file: Union[str, os.PathLike] = None,
    debug=False,
    reverse=False,
    flatten_list=False,
    non_skip=False,
):
    """Compare graphs with url as input. The function will judge whether two graphs are the reused and identical.
    It will record different nodes, compare url and different detail.

    :param job_url1: Pipeline run URL
    :type: str
    :param job_url2: Pipeline run URL
    :type: str
    :param target_file: Path to export the graph compare detail. If not specified, "generated_diff_files.json"
    will be set as default
    :type: Union[str, os.PathLike]
    :param debug: Determines whether to show detailed debug information, default to be false.
    :type debug: bool
    :param reverse: Determines whether to compare graphs with reversed topological sorting, default to be false.
    :type reverse: bool
    :param flatten_list: Whether to flatten the diff result of the list, default is False.
    :type: bool
    :param non_skip: Won't skip fields or modified fields under specific rule, default is False.
    :type: bool
    """
    try:
        from mldesigner._compare._compare_impl import _compare
    except ImportError as e:
        err_msg = f"""Please install compare extra dependencies by running pip install mldesigner[pipeline],
                    currently got {e}"""
        raise UserErrorException(err_msg)
    if not target_file:
        target_file = "generated_diff_files.json"
    if private_features_enabled():
        from mldesigner._azure_ai_ml import try_enable_internal_components

        try_enable_internal_components()
        return _compare(
            job_url1=job_url1,
            job_url2=job_url2,
            target_file=target_file,
            debug=debug,
            reverse=reverse,
            flatten_list=flatten_list,
            non_skip=non_skip,
        )
    err_msg = (
        "Graph compare is a private feature in mldesigner, please set environment variable "
        "AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED to true to use it."
    )
    raise UserErrorException(err_msg)
