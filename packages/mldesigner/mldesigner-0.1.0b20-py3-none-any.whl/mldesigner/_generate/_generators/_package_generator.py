# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from pathlib import Path
from typing import Dict, List, Optional

from mldesigner._azure_ai_ml import Component
from mldesigner._generate._generate_package import generate_pkg_logger
from mldesigner._generate._generators._doc_generator import DocGenerator
from mldesigner._generate._generators._module_generator import ModuleGenerator
from mldesigner._generate._generators._setup_generator import SetupGenerator


class PackageGenerator:
    SETUP_FILE_NAME = "setup.py"

    def __init__(
        self,
        package_name: Optional[str],
        assets: dict,
        working_dir: Path,
        pattern_to_components: Dict[str, List[Component]],
        force_regenerate=False,
    ):
        self._package_name = package_name
        self._assets = assets
        self._working_dir = working_dir
        self._pattern_to_components = pattern_to_components
        self._force_regenerate = force_regenerate
        self.errors = []

    def generate_module(self, target_dir: Path):
        for module_name, asset_list in self._assets.items():
            generator = ModuleGenerator(
                assets=asset_list,
                working_dir=self._working_dir,
                target_dir=target_dir,
                module_name=module_name,
                force_regenerate=self._force_regenerate,
                pattern_to_components=self._pattern_to_components,
            )
            generator.generate(target_dir=target_dir)
            self.errors += generator.errors

    def generate(self):
        if not self._assets:
            return
        if self._package_name:
            # generate package
            target_package_dir = self._working_dir / self._package_name
            if target_package_dir.exists():
                if not self._force_regenerate:
                    msg = f"Skip generating package {target_package_dir.as_posix()} since it's already exists."
                    generate_pkg_logger.warning(msg)
                    return
            else:
                target_package_dir.mkdir(parents=True)

            # package tree structure:
            package_tree = self._package_name.replace("-", os.sep)
            os.makedirs(os.path.join(target_package_dir, package_tree), exist_ok=True)
            # step into inner folder
            source_dir = target_package_dir
            for folder_name in package_tree.split(os.sep):
                source_dir = os.path.join(source_dir, folder_name)
                # attach __init__.py
                Path(os.path.join(source_dir, "__init__.py")).touch(exist_ok=True)

            # module in package
            self.generate_module(target_dir=target_package_dir / package_tree)
            # setup
            SetupGenerator(package_name=self._package_name).generate_to_file(target_package_dir / self.SETUP_FILE_NAME)
            # doc
            DocGenerator(package_name=self._package_name).generate(target_dir=target_package_dir / "doc")
        else:
            # generate module
            self.generate_module(target_dir=self._working_dir)
