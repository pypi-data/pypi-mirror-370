# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import Counter
from typing import Dict

from mldesigner._azure_ai_ml import Component
from mldesigner._generate._generators._base_component_generator import BaseComponentGenerator
from mldesigner._generate._generators._base_generator import BaseGenerator
from mldesigner._generate._generators._constants import NODE_TO_NAME, V1_COMPONENT_TO_NODE, V2_COMPONENT_TO_NODE


class SingleComponentEntityGenerator(BaseGenerator, BaseComponentGenerator):
    def __init__(self, component_entity, unique_name: str = None):
        super(SingleComponentEntityGenerator, self).__init__(component_entity=component_entity, unique_name=unique_name)

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "single_component_entity.template"

    @property
    def entry_template_keys(self) -> list:
        return ["component_cls_name", "component_type_cls", "inputs", "outputs", "enums"]


class ComponentImplGenerator(BaseGenerator):
    def __init__(self, name_to_components: Dict[str, Component]):
        self._component_entities = name_to_components.values()
        # check used components
        self.v2_node_cls, self.v1_node_cls = self._get_used_components(components=self._component_entities)

        self._component_ids = [f"{c.name}:{c.version}" for c in self._component_entities]
        self._component_entity_generators = [
            SingleComponentEntityGenerator(component_entity=val, unique_name=key)
            for key, val in name_to_components.items()
        ]

    @classmethod
    def _get_used_components(cls, components):
        v2_node_cls, v1_node_cls = [], []

        used_components_counter = Counter(map(lambda c: c.type, components))

        for v2_component, v2_node in V2_COMPONENT_TO_NODE.items():
            if v2_component in used_components_counter:
                v2_node_cls.append(v2_node.__name__)

        for v1_component, v1_node in V1_COMPONENT_TO_NODE.items():
            # may need to rename v1 node since there will be conflict with v2 nodes, eg: Command, Parallel
            if v1_component in used_components_counter:
                if v1_node.__name__ == NODE_TO_NAME[v1_node]:
                    item = v1_node.__name__
                else:
                    item = f"{v1_node.__name__} as {NODE_TO_NAME[v1_node]}"
                v1_node_cls.append(item)
        return sorted(v2_node_cls), sorted(set(v1_node_cls))

    @property
    def tpl_file(self):
        return self.TEMPLATE_PATH / "_components_impl.template"

    @property
    def builtin_imports(self):
        return ["from enum import Enum"]

    @property
    def third_party_imports(self):
        imports = ["from azure.ai.ml import Input, Output"]
        if self.v2_node_cls:
            imports.append(f"from azure.ai.ml.entities._builders import {', '.join(self.v2_node_cls)}")
        if self.v1_node_cls:
            imports.append(f"from azure.ai.ml._internal.entities import {', '.join(self.v1_node_cls)}")
        return imports

    @property
    def component_ids(self):
        return self._component_ids

    @property
    def component_defs(self):
        return [g.generate() for g in self._component_entity_generators]

    @property
    def entry_template_keys(self) -> list:
        return [
            "builtin_imports",
            "third_party_imports",
            "component_ids",
            "component_defs",
        ]
