# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
from pathlib import Path
from typing import Dict

from mldesigner._azure_ai_ml import Component
from mldesigner._generate._generators._base_component_generator import BaseComponentGenerator
from mldesigner._generate._generators._base_generator import BaseGenerator


class SingleComponentReferenceGenerator(BaseGenerator, BaseComponentGenerator):
    def __init__(self, component_entity: Component, module_dir: Path, unique_name: str = None):
        super(SingleComponentReferenceGenerator, self).__init__(
            component_entity=component_entity, unique_name=unique_name
        )
        self._module_dir = Path(module_dir).absolute()

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "single_component_reference.template"

    @property
    def ref_params(self):
        component = self._entity
        if component._source_path:
            module_dir = Path(self._module_dir)
            source_path = Path(component._source_path).absolute()
            relative_path = Path(os.path.relpath(source_path, module_dir)).as_posix()
            return {"path": f"current_folder / {repr(relative_path)}"}
        try:
            from mldesigner._generate._generate_package_impl import AssetsUtil

            # Component is a registry component.
            result = AssetsUtil.match_registry(asset=component.id)
            return {"name": repr(component.name), "version": repr(component.version), "registry": repr(result[0])}
        except Exception:  # pylint: disable=broad-except
            # Component is a workspace registered component.
            return {"name": repr(component.name), "version": repr(component.version)}

    @property
    def entry_template_keys(self) -> list:
        return [
            "ref_params",
            "component_func_name",
            "component_cls_name",
            "description",
            "enums",
            "inputs",
            "outputs",
        ]


class ComponentReferenceGenerator(BaseGenerator):
    def __init__(self, name_to_components: Dict[str, Component], module_dir):
        self._component_entities = name_to_components.values()
        self._ref_generators = [
            SingleComponentReferenceGenerator(component_entity=val, module_dir=module_dir, unique_name=name)
            for name, val in name_to_components.items()
        ]
        entities = [f"{c.component_cls_name}Component" for c in self._ref_generators]
        enums = [e.enum_cls_name for c in self._ref_generators for e in c.enums]
        self._components_impl_imports = sorted(entities + enums)

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_components.template"

    @property
    def builtin_imports(self):
        return [
            "from pathlib import Path",
        ]

    @property
    def third_party_imports(self):
        return [
            "from azure.ai.ml import Input",
            "from mldesigner import reference_component",
        ]

    @property
    def components_impl_imports(self):
        return self._components_impl_imports

    @property
    def component_funcs(self):
        return [g.generate() for g in self._ref_generators]

    @property
    def component_func_names(self):
        return [g.component_func_name for g in self._ref_generators]

    @property
    def entry_template_keys(self) -> list:
        return [
            "builtin_imports",
            "third_party_imports",
            "components_impl_imports",
            "component_funcs",
        ]
