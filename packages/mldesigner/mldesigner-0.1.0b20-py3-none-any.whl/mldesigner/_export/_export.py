# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List
from mldesigner._exceptions import UserErrorException


def export(source: str, include_components: List[str] = None):
    """Export pipeline source to code.

    :param source: Pipeline job source, currently supported format is pipeline run URL
    :param include_components: Included components to download snapshot.
        Use * to export all components,
        Or list of components used in pipeline.
        If not specified, all components in pipeline will be exported without downloading snapshot.
    :return:
    """
    try:
        from mldesigner._export._export_impl import _export
    except ImportError as e:
        err_msg = f"""Please install generate extra dependencies by running pip install mldesigner[pipeline],
                    currently got {e}"""
        raise UserErrorException(err_msg)

    return _export(source=source, include_components=include_components)
