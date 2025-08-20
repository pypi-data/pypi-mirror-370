# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import glob
import logging
import os
import sys
import types
from pathlib import Path
from types import FunctionType
from typing import Union

from mldesigner._azure_ai_ml import Component, load_component
from mldesigner._compile._compile import compile_logger
from mldesigner._compile._compile_collector import CompileCollector
from mldesigner._compile._component_compiler import (
    CommandComponentCompiler,
    ParallelComponentCompiler,
    SparkComponentCompiler,
)
from mldesigner._compile._internal_component_compiler import InternalComponentCompiler
from mldesigner._compile._pipeline_component_compiler import PipelineComponentCompiler
from mldesigner._compile._promptflow_component_compiler import PromptflowComponentCompiler
from mldesigner._constants import NodeType
from mldesigner._exceptions import MldesignerCompileError, ValidationException
from mldesigner._utils import (
    _is_dsl_pipeline_function,
    _is_mldesigner_component_function,
    _is_variable_args_function,
    is_internal_component,
)


def _compile(
    source: Union[str, FunctionType],
    *,
    name=None,
    output=None,
    ignore_file=None,
    debug=False,
    **kwargs,  # pylint: disable=unused-argument
):
    """Compile sdk-defined components/pipelines to yaml files, or build yaml components/pipelines with snapshot"""
    total_files = 0
    # a collector is used to extract components/pipelines from source file,
    # also work as an overall context manager to manage these compile targets during the compile process
    collector = CompileCollector(output=output, ignore_file=ignore_file)

    # set log handler level
    if debug is True:
        for log_handler in compile_logger.handlers:
            if isinstance(log_handler, logging.StreamHandler):
                log_handler.setLevel(logging.DEBUG)

    # Logs about basic information
    _log_basic_compile_information(source, name, output)

    if isinstance(source, str):
        files = glob.glob(source, recursive=True)
        # filter out valid input files
        valid_suffix = [".py", ".yaml", ".yml"]
        files = [file for file in files if Path(file).suffix in valid_suffix]
        total_files = len(files)
        compile_logger.info("Found %s files with valid suffix (.py/.yaml/.yml) from input: '%s'", total_files, source)
        for index, file in enumerate(files):
            compile_logger.debug("[%s/%s] Compiling '%s':", index + 1, total_files, file)
            _compile_from_single_file(
                file=file,
                collector=collector,
                component_name=name,
            )
    elif isinstance(source, os.PathLike):
        total_files = 1
        compile_logger.debug("Compiling '%s':", Path(source).resolve().absolute())
        _compile_from_single_file(
            file=source,
            collector=collector,
            component_name=name,
        )
    elif isinstance(source, FunctionType):
        compile_logger.debug("Compiling target function: %s", source.__name__)
        _compile_from_single_function(
            func=source,
            collector=collector,
        )
    else:
        raise MldesignerCompileError(
            f"Source must be a component/pipeline function or a file path str, got {type(source)}"
        )

    # Logs about summary info. Details will be shown if user sets debug mode
    _log_compile_summary_info(collector=collector, total_files=total_files)


# pylint: disable=broad-except
def _compile_from_single_file(file, collector: CompileCollector, component_name=None, raise_error=False):
    """Compile components from a specified file source

    Note:
        raise_error is a flag for devs to local debug compile logic, if specified as true, any compile error will
        stop the whole compile process and get raised with full stack trace
        This flag should always be FALSE before merging into master branch
    """
    file_suffix = Path(file).suffix

    if file_suffix == ".py":
        try:
            components = collector._collect_compile_components_from_file(input_file=file, component_name=component_name)
        except Exception as e:
            collector._update_failed_source_file(file, str(e))
            if raise_error:
                raise
        else:
            total_components = len(components)
            additional_info = "" if not component_name else f" with name '{component_name}'"
            compile_logger.debug("Found %s available components%s.", total_components, additional_info)
            for component in components:
                try:
                    _compile_from_single_component_or_pipeline(component=component, collector=collector)
                except Exception as e:
                    collector._update_failed_component(component, str(e))
                    if raise_error:
                        raise

    elif file_suffix in [".yaml", ".yml"]:
        # if no output specified, update yaml input as failed source file
        if not collector._output:
            error_msg = "No output folder specified for yaml component input file."
            collector._update_failed_source_file(file, error_msg)
            return

        try:
            component = load_component(source=file)
        except Exception as e:
            error_msg = f"Error when loading target yaml: {str(e)}"
            collector._update_failed_source_file(file, error_msg)
            if raise_error:
                raise
        else:
            # if component name is not target component, return
            if component_name and component.name != component_name:
                compile_logger.debug("Yaml component name is not target specified name '%s', skipped.", component_name)
                return
            # yaml pipeline component is not supported yet
            if component.type == NodeType.PIPELINE:
                error_msg = "Yaml pipeline component is not supported."
                collector._update_failed_component(component, error_msg)
                if raise_error:
                    raise MldesignerCompileError(error_msg)
                return

            try:
                _compile_from_single_component_or_pipeline(component=component, collector=collector)
            except Exception as e:
                collector._update_failed_component(component, str(e))
                if raise_error:
                    raise
    else:
        error_msg = f"Unsupported file suffix '{file_suffix}', should be one of ['.py', '.yaml', '.yml']."
        collector._update_failed_source_file(file, error_msg)


def _compile_from_single_function(func: types.FunctionType, collector: CompileCollector):
    """Compile component from a specified function source"""
    if _is_variable_args_function(func):
        raise ValidationException("Not support compile variable args function.")
    if _is_dsl_pipeline_function(func):
        if func._pipeline_builder.non_pipeline_parameter_names:
            raise ValidationException("Not support compile pipeline func with non-pipeline-input.")
        component = func._pipeline_builder.build()
    elif _is_mldesigner_component_function(func):
        component = func.component
    else:
        raise ValidationException("Function is not a valid dsl pipeline function.")

    _compile_from_single_component_or_pipeline(component, collector)


def _compile_from_single_component_or_pipeline(
    component: Component,
    collector: CompileCollector,
):
    """Compile a component or pipeline component to yaml files"""
    node_type = component.type
    if node_type == NodeType.COMMAND:
        compiler = CommandComponentCompiler(component, collector)
    elif node_type == NodeType.PIPELINE:
        compiler = PipelineComponentCompiler(component, collector)
    elif is_internal_component(component):
        compiler = InternalComponentCompiler(component, collector)
    elif node_type in [NodeType.FLOW_PARALLEL]:
        compiler = PromptflowComponentCompiler(component, collector)
    elif node_type == NodeType.PARALLEL:
        compiler = ParallelComponentCompiler(component, collector)
    elif node_type == NodeType.SPARK:
        compiler = SparkComponentCompiler(component, collector)
    else:
        raise MldesignerCompileError(
            f"Unsupported node type '{node_type}' when compiling component '{component.name}'."
        )

    compiler.compile()
    collector._move_compiled_files_to_dest()


def _log_basic_compile_information(source, name, output):
    """Log basic compile information"""
    compile_logger.debug("Mldesigner parsing compile source: %s", source)
    if name is None:
        compile_logger.debug("No component/pipeline name specified, will compile all available targets.")
    else:
        compile_logger.debug("Target component/pipeline name: %s", name)

    if output is None:
        compile_logger.debug(
            "No output is specified, will compile component/pipeline to the same folder with source file"
        )
    else:
        compile_logger.debug(
            "Output is specified, will compile component/pipeline to %s with snapshots",
            output,
        )


def _log_compile_summary_info(collector: CompileCollector, total_files: int):

    failed_file_cnt = len(collector._failed_candidate_files)
    successful_files = total_files - failed_file_cnt
    failed_component_cnt = len(collector._failed_candidate_components)
    succeeded_component_cnt = len(collector._successful_candidates)

    compile_logger.debug("=================================== Summary ===================================")
    # log failed files
    if failed_file_cnt != 0:
        compile_logger.info("[Failed Files] %s files failed to be compiled:", failed_file_cnt)
        for file, error_msg in collector._failed_candidate_files.items():
            compile_logger.info("    '%s': '%s'", file, error_msg)

    # log failed components
    if failed_component_cnt != 0:
        compile_logger.info("[Failed components] %s components failed to be compiled:", failed_component_cnt)
        for name, compile_task in collector._failed_candidate_components.items():
            compile_logger.info("    '%s': '%s'", name, compile_task.error_msg)

    # log successful components
    if succeeded_component_cnt != 0:
        compile_logger.debug("[Successful components] %s components succeeded.", succeeded_component_cnt)
        for name, compile_task in collector._successful_candidates.items():
            file_name = Path(compile_task.source).name
            compile_logger.debug("    [Compiled] %s -> %s", file_name, name)

    additional_info = f" from {successful_files} files" if total_files > 0 else ""
    additional_info_2 = (
        f" Skipped {failed_file_cnt} files and {failed_component_cnt} components."
        if failed_file_cnt + failed_component_cnt > 0
        else ""
    )
    summary_info = f"Mldesigner has compiled {succeeded_component_cnt} components{additional_info}.{additional_info_2}"
    compile_logger.info(summary_info)

    # exit code to be 1 if there is failed case
    exit_code = 1 if failed_file_cnt or failed_component_cnt else 0
    if exit_code:
        print(f"Mldesigner compile command finished with exit code {exit_code}")
        sys.exit(exit_code)
