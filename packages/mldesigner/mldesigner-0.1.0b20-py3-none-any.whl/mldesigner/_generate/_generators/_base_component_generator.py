# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from collections import OrderedDict

from mldesigner._azure_ai_ml import Component, Input, Output
from mldesigner._exceptions import UserErrorException
from mldesigner._generate._generators._constants import COMPONENT_TO_NODE, NODE_TO_NAME
from mldesigner._generate._generators._param_generator import EnumGenerator, ParamGenerator
from mldesigner._utils import _sanitize_python_class_name, _sanitize_python_variable_name


class BaseComponentGenerator:
    def __init__(self, component_entity: Component, unique_name: str = None):
        self._component_unique_name = unique_name if unique_name else component_entity.name

        self._entity = component_entity
        self._component_type_cls = self._get_component_type_cls()
        self._inputs, self._enums = self._get_component_inputs()
        self._outputs = self._get_component_outputs()

    @property
    def component_name(self):
        return self._component_unique_name

    @property
    def component_func_name(self):
        return _sanitize_python_variable_name(self.component_name)

    @property
    def component_cls_name(self):
        # hide all component entity classes
        return f"_{_sanitize_python_class_name(self.component_name)}"

    @property
    def component_version(self):
        return self._entity.version

    @property
    def component_type_cls(self):
        return self._component_type_cls

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def description(self):
        return self._entity.description or f"{self.component_name}: {self.component_version}"

    @property
    def enums(self):
        return self._enums

    def _get_component_type_cls(self):
        node_cls = COMPONENT_TO_NODE.get(self._entity.type, None)
        # component should be filtered in AssetsUtil.filter_components
        if node_cls is None:
            # pylint: disable=protected-access
            raise UserErrorException(
                f"Unsupported component type: {type(self._entity)} from {self._entity._source_path}"
            )
        node_cls_name = NODE_TO_NAME[node_cls]
        return node_cls_name

    @staticmethod
    def _is_internal_component_enum(var: Input):
        if isinstance(var.type, str):
            return var.type.lower() == "enum"
        if isinstance(var.type, list):
            return "enum" in var.type
        return False

    def _get_component_inputs(self):
        inputs = {}
        enums = []
        for in_name, val in self._entity.inputs.items():
            # keep original input name in generated function stubs
            # because the component function call is case insensitive, but node params are case sensitive
            if isinstance(val, Input):
                if val._is_enum() or self._is_internal_component_enum(val):  # pylint: disable=protected-access
                    generator = EnumGenerator(in_name, val, self.component_cls_name)
                    enums.append(generator)
                else:
                    generator = ParamGenerator(in_name, val)
                inputs[in_name] = generator
            else:
                raise UserErrorException(f"Expecting {type(Input)}, got {type(val)} instead.")

        return OrderedDict(sorted(inputs.items())), enums

    def _get_component_outputs(self):
        outputs = {}
        for out_name, val in self._entity.outputs.items():
            # leave output as it is since we won't change output names
            if isinstance(val, Output):
                outputs[out_name] = ParamGenerator(out_name, val)
            else:
                raise UserErrorException(f"Expecting {type(Output)}, got {type(val)} instead.")

        return OrderedDict(sorted(outputs.items()))
