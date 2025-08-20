# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from mldesigner._generate._generators._base_generator import BaseGenerator


class SetupGenerator(BaseGenerator):
    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "setup.template"

    @property
    def entry_template_keys(self) -> list:
        return ["package_name"]
