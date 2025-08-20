# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin

from types import FunctionType
from typing import Union

from mldesigner._exceptions import UserErrorException
from mldesigner._logger_factory import _LoggerFactory

compile_logger = _LoggerFactory.get_logger("compile")


def compile(
    source: Union[str, FunctionType],
    *,
    name=None,
    output=None,
    ignore_file=None,
    debug=False,
    **kwargs,
):
    """Compile sdk-defined components/pipelines to yaml files, or build yaml components/pipelines with snapshot.

    A component can be defined through sdk using @mldesigner.command_component decorator, and a pipeline can be
    defined using @dsl.pipeline decorator. Such components or pipelines can be compiled into yaml files with mldesigner
    compile function. When the input is already a yaml component/pipeline, "output" parameter is required and mldesigner
    will build a fully-resolved component/pipeline into this specified output folder.


    :param source: Source file or objects to be compiled. Could one of below types:
        * SDK-defined component/pipeline function: The decorated function object.
        * File path with suffix '.py' : The file that contains sdk-defined components or pipelines.
        * File path with suffix '.yaml'(or .yml) : The component/pipeline yaml file.
    :type source: Union[str, FunctionType]
    :param name: The name of target component/pipeline to be compiled.
    :type name: str
    :param output: The folder in which to put compiled results.
        * If not specified, compiled files are in the same folder with source file.
        * If specified, compiled component with its snapshot are in ./{output_folder}/{component_name}/
    :type output: str
    :param ignore_file: The file path that contains ignore patterns, determines what files will be ignored
        during compilation. Only supports '.gitignore' and '.amlignore' file. By default, the compilation
        will use ignore files, in the component code folder. If specified, the specified ignore file will
        be used COMBINED with original ignore files in the component code folder.
    :type ignore_file: Union[str, Path]
    :param debug: Determines whether to show detailed debug information, default to be false.
    :type debug: bool

    """
    # import locally so generate package interface don't depend on azure-ai-ml
    try:
        from mldesigner._compile._compile_impl import _compile
    except ImportError as e:
        err_msg = (
            "Please install compile extra dependencies by running `pip install mldesigner[pipeline]`, "
            f"currently got {e}"
        )
        raise UserErrorException(err_msg)

    return _compile(source=source, name=name, output=output, ignore_file=ignore_file, debug=debug, **kwargs)
