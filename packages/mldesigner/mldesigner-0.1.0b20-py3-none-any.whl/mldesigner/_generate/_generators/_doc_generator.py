# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path

from mldesigner._generate._generators._base_generator import BaseGenerator


class DocConfGenerator(BaseGenerator):
    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "conf.py.template"

    @property
    def entry_template_keys(self) -> list:
        return ["package_name"]


class DocIndexGenerator(BaseGenerator):
    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "index.rst.template"

    @property
    def entry_template_keys(self) -> list:
        return ["package_name"]


class DocGenerator:
    CONF_FILE_NAME = "conf.py"
    INDEX_FILE_NAME = "index.rst"

    def __init__(self, package_name: str):
        self.package_name = package_name

    def generate(self, target_dir: Path):
        target_dir.mkdir(parents=True, exist_ok=True)
        DocConfGenerator(package_name=self.package_name).generate_to_file(target_dir / self.CONF_FILE_NAME)
        DocIndexGenerator(package_name=self.package_name).generate_to_file(target_dir / self.INDEX_FILE_NAME)
