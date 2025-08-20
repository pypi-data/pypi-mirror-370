# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import glob
import hashlib

# pylint: disable=protected-access
import re
from pathlib import Path
from typing import Dict, List
from uuid import UUID

from mldesigner._azure_ai_ml import Component
from mldesigner._utils import _sanitize_python_variable_name
from mldesigner._generate._generate_package import generate_pkg_logger
from mldesigner._generate._generators._components_generator import ComponentReferenceGenerator
from mldesigner._generate._generators._components_impl_generator import ComponentImplGenerator
from mldesigner._generate._generators._init_generator import InitGenerator


def _get_selected_component_name(component):
    """try to use display_name when component name is not clear"""
    if component.display_name and component.name == "azureml_anonymous":
        return component.display_name
    return component.name


def get_unique_component_func_names(components: List[Component]):
    """Try to return unique component func names, raise exception when duplicate component are found."""
    name_to_component = {}
    name_version_to_component = {}
    errors = []

    for component in components:
        selected_name = _get_selected_component_name(component)
        name_version = f"{selected_name}:{component.version}"
        if name_version in name_version_to_component:
            existing_component = name_version_to_component[name_version]
            load_source = [
                existing_component._source_path or existing_component.id,
                component._source_path or existing_component.id,
            ]
            errors.append(f"Duplicate component {name_version} found. Loaded from: {load_source}")
            continue
        name_version_to_component[name_version] = component

        name_candidate = get_unique_component_func_name(name_to_component, component)
        name_to_component[name_candidate] = component
    return name_to_component, errors


def get_unique_component_func_name(existing_names, component):
    component_func_name = _get_selected_component_name(component)
    name_version = f"{component_func_name}:{component.version}"
    name_candidate = _sanitize_python_variable_name(component_func_name)
    if name_candidate not in existing_names:
        return name_candidate

    name_candidate = _sanitize_python_variable_name(name_version)
    if name_candidate not in existing_names:
        return name_candidate

    # if _sanitize_python_variable_name(component_func_name) and _sanitize_python_variable_name(name_version) both exist
    # add hash result behind name_version because current name_version must differ from other name_versions
    hash_value = hashlib.sha256(name_version.encode("utf-8")).hexdigest()
    suffix = str(UUID(hash_value[:32]))
    name_candidate = _sanitize_python_variable_name(f"{name_version}_{suffix}")
    return name_candidate


class ModuleGenerator:
    COMPONENTS_FILE_NAME = "_components.py"
    COMPONENTS_IMPL_FILE_NAME = "_components_impl.py"
    COMPONENTS_INIT_NAME = "__init__.py"

    def __init__(
        self,
        assets: list,
        working_dir: Path,
        target_dir: Path,
        module_name: str,
        pattern_to_components: Dict[str, List[Component]],
        force_regenerate=False,
    ):
        from mldesigner._generate._generate_package_impl import AssetsUtil

        self._components = self._load_components_from_asset_matcher(assets, pattern_to_components)
        self._module_name = module_name
        if all(
            [
                not asset.startswith(AssetsUtil.WORKSPACE_PREFIX) and not asset.startswith(AssetsUtil.REGISTRY_PREFIX)
                for asset in assets
            ]
        ):
            self._local_components_hash = self._hash_files_content(assets)
        else:
            self._local_components_hash = None

        # sort the components so generated file are sorted.
        self._components = sorted(self._components, key=lambda c: f"{c.name}:{c.version}")

        # handle conflicts
        name_to_components, errors = get_unique_component_func_names(self._components)
        self.errors = errors

        self._ref_generator = ComponentReferenceGenerator(
            name_to_components=name_to_components, module_dir=target_dir / self._module_name
        )
        self._impl_generator = ComponentImplGenerator(name_to_components=name_to_components)
        self._init_generator = InitGenerator(
            ref_generator=self._ref_generator, components_hash=self._local_components_hash
        )
        self._working_dir = Path(working_dir)
        self._force_regenerate = force_regenerate

    @classmethod
    def _load_components_from_asset_matcher(cls, assets: list, pattern_to_components: dict):
        components = []
        for asset in assets:
            components += pattern_to_components[asset]
        return components

    @staticmethod
    def _hash_files_content(assets_list):
        """Hash the file content in the file list."""
        ordered_file_list = set()
        for asset in assets_list:
            ordered_file_list.update(list(glob.glob(asset, recursive=True)))
        ordered_file_list = list(ordered_file_list)
        hasher = hashlib.sha256()
        # To avoid reuse the hash code generated by v1.5
        hasher.update(b"mldesigner generate")
        ordered_file_list.sort()
        for item in ordered_file_list:
            with open(item, "rb") as f:
                hasher.update(f.read())
        return hasher.hexdigest()

    def _is_regenerate_module(self, target_module_folder: Path):
        init_path = target_module_folder / self.COMPONENTS_INIT_NAME
        if init_path.exists() and self._local_components_hash:
            with open(init_path, "r") as f:
                assets_spec_code = f.read()
            local_hash_regex = "LOCAL_ASSETS_HASH: (.*)"
            regex_result = re.search(local_hash_regex, assets_spec_code, re.MULTILINE)
            origin_local_asset_hash = regex_result.groups()[0] if regex_result else None
            return self._local_components_hash != origin_local_asset_hash
        return True

    def generate(self, target_dir: Path):
        if not self._components:
            return
        target_module_folder = target_dir / self._module_name
        if not self._force_regenerate and not self._is_regenerate_module(target_module_folder=target_module_folder):
            msg = f"Skip generating module {target_module_folder.as_posix()} since it's already exists."
            generate_pkg_logger.warning(msg)
            return
        target_module_folder.mkdir(parents=True, exist_ok=True)

        self._ref_generator.generate_to_file(target_module_folder / self.COMPONENTS_FILE_NAME)
        self._impl_generator.generate_to_file(target_module_folder / self.COMPONENTS_IMPL_FILE_NAME)
        self._init_generator.generate_to_file(target_module_folder / self.COMPONENTS_INIT_NAME)
