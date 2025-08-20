# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import inspect
import shutil
import tempfile
from pathlib import Path
from typing import Callable

from mldesigner._azure_ai_ml import Component
from mldesigner._constants import AML_IGNORE_SUFFIX, GIT_IGNORE_SUFFIX
from mldesigner._exceptions import ImportException, MldesignerCompileError
from mldesigner._utils import (
    _import_component_with_working_dir,
    _is_dsl_pipeline_function,
    _is_mldesigner_component_function,
    _is_variable_args_function,
)


class CompileCollector:
    """Work as an overall context manager to manage compile targets during the compile process"""

    def __init__(self, output=None, ignore_file=None):
        self._compile_candidates = {}
        self._successful_candidates = {}
        self._failed_candidate_components = {}
        self._failed_candidate_files = {}
        self._temp_dir = tempfile.TemporaryDirectory()
        # determines if compiled files get sent to be with source file or in specified output folder
        self._output = self._validate_output(output)
        # the ignore file path that contains ignore patterns
        self._ignore_file = self._validate_ignore(ignore_file)

    def _collect_compile_components_from_file(self, input_file, component_name):
        py_file = Path(input_file).absolute()
        if py_file.suffix != ".py":
            msg = f"File is not a valid py file: {py_file}"
            raise MldesignerCompileError(message=msg)
        if not py_file.exists():
            msg = f"File does not exist: {py_file}"
            raise MldesignerCompileError(message=msg)

        working_dir = py_file.parent.absolute()
        component_path = py_file.relative_to(working_dir).as_posix().split(".")[0].replace("/", ".")

        components = list(self._collect_compile_targets_from_py_module(component_path, working_dir))
        components = self._remove_duplicates(components)
        if component_name:
            components = [component for component in components if component.name == component_name]

        return components

    def _remove_duplicates(self, components):
        visited = set()
        duplicates = set()
        for component in components:
            name = component.name
            if name not in visited:
                visited.add(name)
            else:
                duplicates.add(name)
                candidate = CompileTask(component)
                candidate.error_msg = f"Duplicate component name {name!r} in source file: {component._source_path}"
                self._failed_candidate_components[name] = candidate

        components = [component for component in components if component.name not in duplicates]
        return components

    @classmethod
    def _validate_output(cls, output):
        """Validate if specified output is a valid folder path and create the folder if not exist"""
        if not output:
            return None

        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @staticmethod
    def _validate_ignore(ignore_file):
        """Validate if specified ignore file is a valid ignore file path"""
        if not ignore_file:
            return None

        ignore_file_path = Path(ignore_file)
        if (
            not ignore_file_path.exists()
            or not ignore_file_path.is_file()
            or ignore_file_path.name not in [GIT_IGNORE_SUFFIX, AML_IGNORE_SUFFIX]
        ):
            msg = (
                f"Ignore file is not valid: {str(ignore_file_path.resolve().absolute())!r}. It either does not exist, "
                f"or is not a file, or does not have a valid file name: {GIT_IGNORE_SUFFIX!r} or {AML_IGNORE_SUFFIX!r}."
            )
            raise MldesignerCompileError(message=msg)
        return ignore_file_path

    @classmethod
    def _collect_compile_targets_from_py_module(cls, py_module, working_dir=None, force_reload=True):
        """Collect all components in a python module and return the components."""
        if isinstance(py_module, str):
            try:
                py_module = _import_component_with_working_dir(py_module, working_dir, force_reload)
            except Exception as e:
                msg = """Error occurs when import component '{}': {}.\n
                Please make sure all dependencies have been installed."""
                raise ImportException(message=msg.format(py_module, e)) from e

        objects_with_source_line_order = sorted(
            inspect.getmembers(py_module, inspect.isfunction), key=lambda x: inspect.getsourcelines(x[1])[1]
        )

        for _, obj in objects_with_source_line_order:
            # Skip compile variable args function
            if not _is_variable_args_function(obj):
                if _is_mldesigner_component_function(obj):
                    yield obj.component
                elif _is_dsl_pipeline_function(obj):
                    # Skip the pipeline with non-pipeline-inputs
                    if not obj._pipeline_builder.non_pipeline_parameter_names:
                        yield obj._pipeline_builder.build()

    def _update_compile_candidate(self, component: Component):
        candidate = CompileTask(component)
        self._compile_candidates[component.name] = candidate

    def _update_failed_source_file(self, file, msg):
        self._clean_up_collector()
        file_name = str(Path(file).absolute())
        self._failed_candidate_files[file_name] = msg

    def _update_failed_component(self, component: Component, msg):
        self._clean_up_collector()
        failed_task = CompileTask(component)
        failed_task.error_msg = msg
        self._failed_candidate_components[component.name] = failed_task

    @classmethod
    def _is_identical_directory(cls, source, dest):
        """Check if source folder and dest folder have identical files and sub directories recursively"""
        # Currently only check file structure, may check file contents in the future
        source_content = [file.relative_to(source) for file in Path(source).glob("**/*")]
        dest_content = [file.relative_to(dest) for file in Path(dest).glob("**/*")]
        return source_content == dest_content

    def _move_compiled_files_to_dest(self):
        """Move all compiled files to dest after the compilation succeeds"""
        # check if component with different content already exist in specified output folder
        if self._output:
            candidates = copy.deepcopy(self._compile_candidates)
            for name, candidate in candidates.items():
                temp_component_folder = Path(self._temp_dir.name) / name
                dest_dir = self._output / name
                if dest_dir.exists():
                    # will fail if compiling different component with the same name
                    if self._is_identical_directory(temp_component_folder, dest_dir):
                        self._successful_candidates[name] = self._compile_candidates.pop(name)
                    else:
                        raise MldesignerCompileError(
                            f"Component folder '{name}' with different content already in specified output folder: "
                            f"{self._output.resolve().absolute()}"
                        )

        # move compiled files from temp folder to specified folder
        for name, candidate in self._compile_candidates.items():
            temp_component_folder = Path(self._temp_dir.name) / name
            if self._output:
                dest_dir = Path(self._output / name)
                shutil.move(str(temp_component_folder), str(dest_dir))
            else:
                file_name = f"{name}.yaml"
                source = temp_component_folder / file_name
                dest = Path(candidate.source).parent / file_name
                shutil.move(str(source), str(dest))
            self._successful_candidates[name] = candidate

        self._clean_up_collector()

    def _clean_up_collector(self):
        """Clean up the collector when one compile has succeeded or failed"""
        # clean up all compile candidates
        self._compile_candidates = {}

        # clean up files in temp directory
        for path in Path(self._temp_dir.name).glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    def _validate_compile_target(self, component: Component):
        """Validate component target"""
        name = component.name
        source_path = component._source_path

        # component compilation failed before
        failed_candidate = self._failed_candidate_components.get(name, None)
        if failed_candidate and failed_candidate.source == source_path:
            raise MldesignerCompileError(message=failed_candidate.error_msg)

        # when compiling a pipeline, component with same name but different source file is not allowed
        compile_candidate = self._compile_candidates.get(name, None)
        if compile_candidate and compile_candidate.source != source_path:
            msg = "Pipeline has multiple components with same name but different source."
            raise MldesignerCompileError(message=msg)

    def compile_with_data(
        self,
        component: Component,
        dump_component_yaml: Callable,
        copy_snapshot: Callable,
    ) -> Path:
        """Generate component yaml file using input data dict"""
        self._validate_compile_target(component)

        # give an extra layer named by component name
        dest_folder = Path(self._temp_dir.name) / component.name

        # if this component folder already exists, then it must be an identical component so that we can reuse it
        # _validate_compile_target() has guaranteed this, if same component with different source, error will be raised
        if not dest_folder.exists():
            dest_folder.mkdir(parents=True, exist_ok=True)

            dump_component_yaml(dest_folder)
            self._update_compile_candidate(component)
            if self._output:
                copy_snapshot(dest_folder)

        return dest_folder


class CompileTask:
    """Task class that stores component meta info during compile process"""

    def __init__(self, component):
        self.name = component.name
        self.source = component._source_path
        self.error_msg = None
