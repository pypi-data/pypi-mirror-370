# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import shutil
from pathlib import Path

import yaml

from mldesigner._azure_ai_ml import Component
from mldesigner._compile._compile_collector import CompileCollector
from mldesigner._compile._ignore_file import ComponentIgnoreFile, IgnoreFile
from mldesigner._compile._utils import get_upload_files_from_folder
from mldesigner._constants import ComponentSource, IoConstants
from mldesigner._exceptions import MldesignerCompileError
from mldesigner._utils import _remove_empty_key_in_dict, is_internal_component


class BaseCompiler:
    """Base compiler to compile SDK-defined components to yaml components"""

    SCHEMA_KEY = "$schema"
    CODE_KEY = "code"

    def __init__(self, component: Component, collector: CompileCollector):
        self._validate_component(component)
        self._component = component
        self._collector = collector
        self._output = collector._output
        # component content should be component dict which is generated in _update_compile_content function
        self._component_content = None
        # snapshot are all the dependency files needed for a component
        self._snapshot = None

    def compile(self):
        self._update_compile_content()
        self._collector.compile_with_data(
            component=self._component,
            dump_component_yaml=self._dump_component_yaml,
            copy_snapshot=self._copy_snapshot,
        )

    def _dump_component_yaml(self, dest_folder: Path):
        """Dump component yaml spec to dest_folder.

        Note that here dest_folder is a temporary folder. The snapshot will be copied to the final output folder in
        CompileCollector._move_compiled_files_to_dest.
        """
        if self._component_content is None:
            raise MldesignerCompileError("Component content is empty, nothing to compile.")
        # make sure yaml file keys are ordered
        self._component_content = self._get_reordered_dict(self._component_content)

        component = self._component
        dest_yaml_name = f"{component.name}.yaml"
        if component._source == ComponentSource.YAML_COMPONENT:
            dest_yaml_name = Path(component._source_path).name
        dest_yaml = dest_folder / dest_yaml_name
        # remove empty dict in data
        data = _remove_empty_key_in_dict(self._component_content)
        with open(dest_yaml, "w", encoding="utf-8") as fout:
            yaml.dump(data, fout, sort_keys=False)

    def _copy_snapshot(self, dest_folder: Path):
        """
        Move files in snapshot_list to the destination folder specified by dest_folder.

        :param dest_folder: The destination path to copy the files to.
        :type dest_folder: Union[str, Path]
        :return: A list of tuples, where each tuple contains the original absolute path of a file and the
            new absolute path of the file after it is copied to the destination folder.
        :rtype: Optional[list(tuple(str, str))]
        """

        # snapshot_list: A list of tuples, where each tuple contains an absolute path string of
        # a file and a relative path string which is relative to the dest_folder parameter of the function.
        # type of snapshot_list: list(tuple(str, str))

        # :Example:
        #
        # self._snapshot = [("/a/b/c/d.py", "c/d.py")]
        # _copy_snapshot("/e/f")
        # result: [('/a/b/c/d.py', '/e/f/c/d.py')]

        dest_path = Path(dest_folder)
        snapshot_list = self._snapshot
        if not snapshot_list:
            return None

        # Create any necessary subdirectories in the destination folder
        for _, relative_path in snapshot_list:
            sub_dirs = Path(relative_path).parent
            if sub_dirs:
                Path(dest_path / sub_dirs).mkdir(parents=True, exist_ok=True)

        # Copy files to destination folder and create a list of tuples with original and new paths
        new_paths = []
        for absolute_path, relative_path in snapshot_list:
            new_absolute_path = dest_path / relative_path
            shutil.copy2(absolute_path, new_absolute_path)
            new_paths.append((absolute_path, str(new_absolute_path)))

        return new_paths

    @classmethod
    def _validate_component(cls, component):
        result = component._customized_validate()
        if not result.passed:
            raise MldesignerCompileError(message=result.error_messages)

    @classmethod
    def _update_component_inputs(cls, component_dict):
        """Transform dumped component input value to corresponding type"""
        keys = ["default", "min", "max"]
        inputs = component_dict.get("inputs", {})

        # better way to handle this issue is to change ParameterSchema to use dumpable integer/float/string
        # however this change has a large impact in current code logic, may investigate this as another work item
        for _, input_dict in inputs.items():
            for key in keys:
                if key in input_dict and input_dict["type"] in IoConstants.PARAM_PARSERS:
                    param_parser = IoConstants.PARAM_PARSERS[input_dict["type"]]
                    correct_value = param_parser(input_dict[key])
                    input_dict[key] = correct_value

    @classmethod
    def _refine_component_environment(cls, component_dict: dict):
        """Pop name and version for environment"""
        if "environment" in component_dict and isinstance(component_dict["environment"], dict):
            env = component_dict["environment"]
            env.pop("name", None)
            env.pop("version", None)
            if "conda_file" in env and isinstance(env["conda_file"], dict):
                env["conda_file"].pop("name", None)
                env["conda_file"].pop("version", None)

    def _update_compile_content(self):
        """Update component content and snapshot which will be compiled, implemented by sub-compilers"""
        raise NotImplementedError()

    def _get_reordered_dict(self, original_dict):
        """Make sure dict keys are in order when getting dumped"""
        KEY_ORDER = [
            BaseCompiler.SCHEMA_KEY,
            "name",
            "display_name",
            "description",
            "type",
            "version",
            "is_deterministic",
            "tags",
            "component",
            "inputs",
            "outputs",
            "code",
            "environment",
            "command",
            "jobs",
        ]

        original_dict = copy.deepcopy(original_dict)
        new_dict = {}
        for key in KEY_ORDER:
            if key in original_dict:
                new_dict[key] = original_dict.pop(key)

        # for pipeline component yaml, need to sort job node dict and node's component dict
        if "jobs" in new_dict and isinstance(new_dict["jobs"], dict):
            for node_name, node_dict in new_dict["jobs"].items():
                if "component" in node_dict and isinstance(node_dict["component"], dict):
                    node_dict["component"] = self._get_reordered_dict(node_dict["component"])
                new_dict["jobs"][node_name] = self._get_reordered_dict(new_dict["jobs"][node_name])

        # in case there are missed keys in original dict
        new_dict.update(original_dict)
        return new_dict

    def _get_component_snapshot(self, code):
        """Generate a list that contains all dependencies of a component"""
        # TODO: it is a little wired that this function is never called in base compiler
        # the code could be None, and in that case no snapshot should be included, except additional includes
        if code is not None and not Path(code).is_absolute():
            source_path = Path(self._component._source_path)
            code = source_path.parent / code

        # filter snapshot to exclude ignored files
        snapshot_list = self._get_snapshot_without_ignored_files(code)

        # remove original yaml file if the input is yaml as we need to update code to "."
        # and output new yaml with original file name
        if self._component._source == ComponentSource.YAML_COMPONENT:
            original_yaml = Path(self._component._source_path).resolve().as_posix()
            snapshot_list = [item for item in snapshot_list if item[0] != original_yaml]

        return snapshot_list

    def _get_additional_includes(self):
        """Get a list of additional includes for the component"""
        res = []

        if not isinstance(self._component, Component):
            return res

        if is_internal_component(self._component):
            # internal components are inherited from AdditionalIncludesMixin but original
            # additional include configs can be of artifact, so need to use private interface
            # to get resolved additional includes
            # will update this after
            additional_includes_obj = self._component._additional_includes
            if additional_includes_obj and additional_includes_obj.with_includes:
                code_path = additional_includes_obj.code_path
                res = [Path(code_path / file).resolve().as_posix() for file in additional_includes_obj.includes]
        elif hasattr(self._component, "additional_includes"):
            # among v2 components, only command component and flow component supports additional
            # includes for now, but below code is compatible with other component types once
            # they support additional includes
            base_path = Path(self._component.base_path)
            res = []
            for file in self._component.additional_includes:
                file_path = Path(file)
                if not file_path.is_absolute():
                    file_path = base_path / file_path
                res.append(file_path.resolve().as_posix())

        return res

    def _get_snapshot_without_ignored_files(self, code):
        """Get snapshot without ignored files

        Besides the .amlignore/.gitignore in the code folder, need also check the extra ignore file
        which is stored in collector.

        Returned list consists of elements that are tuples which contains (File absolute path, File relative path)
        """
        resolved_snapshot_list = []
        additional_includes = self._get_additional_includes()
        source_folder = Path(self._component._source_path).parent

        # if code is not None, update the source_folder to extract ignore file
        if code is not None:
            source_folder = Path(code).resolve()

        # extract ignore files in source folder, along with extra ignore list
        extra_ignore_file = self._collector._ignore_file
        extra_ignore_list = [IgnoreFile(extra_ignore_file)] if extra_ignore_file is not None else []
        ignore_file = ComponentIgnoreFile(
            directory_path=source_folder,
            extra_ignore_list=extra_ignore_list,
        )

        # filter out all ignored files for additional includes
        for item in additional_includes:
            item = Path(item)
            if not item.exists():
                continue

            # for folder item, need to filter out the ignored files recursively
            if item.is_dir():
                prefix = item.resolve().name + "/"
                resolved_snapshot_list += get_upload_files_from_folder(
                    path=item, prefix=prefix, ignore_file=ignore_file
                )
            # for file item, make sure it's not on the ignore list
            elif not ignore_file.is_file_excluded(item):
                resolved_snapshot_list.append((item.resolve().as_posix(), "."))

        # filter out ignored files for code folder
        if code is not None:
            resolved_snapshot_list += get_upload_files_from_folder(path=code, ignore_file=ignore_file)

        # remove duplicate paths
        resolved_snapshot_list = list(set(resolved_snapshot_list))

        # remove the files that have suffix ".additional_includes"
        resolved_snapshot_list = [
            item for item in resolved_snapshot_list if not item[0].endswith(".additional_includes")
        ]

        return resolved_snapshot_list
