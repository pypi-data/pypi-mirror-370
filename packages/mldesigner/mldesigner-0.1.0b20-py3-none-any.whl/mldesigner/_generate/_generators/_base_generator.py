# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Template


class BaseGenerator(ABC):
    """Base generator class to generate code/file based on given template."""

    TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates"

    @property
    @abstractmethod
    def tpl_file(self):
        """Specify the template file for different generator."""

    @property
    @abstractmethod
    def entry_template_keys(self) -> list:
        """Specify the entry keys in template, they will be formatted by value when generate code/file."""

    def generate(self) -> str:
        """Generate content based on given template and actual value of template keys."""
        with open(self.tpl_file) as f:
            entry_template = f.read()
            entry_template = Template(entry_template, trim_blocks=True, lstrip_blocks=True)

        return entry_template.render(**{key: getattr(self, key) for key in self.entry_template_keys})

    def generate_to_file(self, target):
        """Generate content to a file based on given template and actual value of template keys."""
        with open(target, "w", encoding="utf-8") as fout:
            fout.write(self.generate())
