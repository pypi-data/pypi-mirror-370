# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import defaultdict
from typing import Union

from mldesigner._azure_ai_ml import Input, Output
from mldesigner._constants import SupportedParameterTypes
from mldesigner._utils import _sanitize_python_class_name, _sanitize_python_variable_name

# pylint: disable=protected-access


class ParamGenerator:
    def __init__(self, name: str, param: Union[Input, Output]):
        self._name = name
        self._param = param

        if isinstance(param, Input):
            self._is_input = True
        elif isinstance(param, Output):
            self._is_input = False

        self._arg_type = self._get_arg_type()
        self._comment = self._get_comment()

    def _get_arg_type(self):
        param = self._param
        if isinstance(param, Input):
            if self.is_port():
                # For other type, use Input
                return "Input"
            return param._get_python_builtin_type_str()
        if isinstance(param, Output):
            return "Output"

    def _get_comment(self):
        """Returns comment for current param."""
        comment_str = self.description.replace('"', '\\"')
        hint_item = ["optional"] if self.optional is True else []
        hint_item.extend(
            [f"{key}: {val}" for key, val in zip(["min", "max", "enum"], [self.min, self.max, self.enum]) if val]
        )
        hint_str = ", ".join(hint_item)
        if hint_str:
            return f"{comment_str} ({hint_str})"
        return f"{comment_str}"

    def is_enum(self):
        return self._param._is_enum

    def has_default(self):
        return self.default is not None

    @property
    def default(self):
        result = self._param.get("default")
        if result is not None and self._param.type.lower() == SupportedParameterTypes.STRING:
            result = repr(result)
        return result

    @property
    def optional(self) -> bool:
        return self._is_input and self._param.optional

    @property
    def min(self):
        return self._param.get("min")

    @property
    def max(self):
        return self._param.get("max")

    @property
    def enum(self):
        return self._param.get("enum")

    @property
    def description(self):
        # self._param.type can be a list of types, e.g. ["AnyFile", "AnyDirectory"]
        default_description = self._param.description or str(self._param.type)
        if self.is_port():
            default_description += f" (type: {self._param.type})"
        return default_description

    @property
    def var_name(self):
        return _sanitize_python_variable_name(self._name)

    @property
    def arg_type(self):
        return self._arg_type

    @property
    def comment(self):
        return self._comment

    def is_port(self):
        """If input/output is not literal, fallback to Input/Output"""
        return not self._param._is_literal()


class EnumGenerator(ParamGenerator):
    def __init__(self, name: str, param: Input, component_cls_name):
        self._component_cls_name = component_cls_name
        super(EnumGenerator, self).__init__(name=name, param=param)
        self._enum_option_key_map = self._init_enum_key_map()

    def _get_arg_type(self):
        return self.enum_cls_name

    @property
    def component_cls_name(self):
        return self._component_cls_name

    @property
    def enum_cls_name(self):
        return f"{self.component_cls_name}{_sanitize_python_class_name(self.var_name)}"

    @property
    def default(self):
        result = self._param.get("default")
        if result:
            return f"{self.enum_cls_name}.{self._get_enum_key(result)}"
        return None

    @classmethod
    def update_name_for_options(cls, option_pairs, filter_func, enum_option_key_map):
        left_option_pairs = []
        for option, sanitized_option in option_pairs:
            if sanitized_option not in enum_option_key_map and filter_func(option, sanitized_option):
                enum_option_key_map[sanitized_option] = option
            else:
                left_option_pairs.append((option, sanitized_option))
        return left_option_pairs

    def _init_enum_key_map(self) -> dict:
        """
        Init a dict of option: var_name
        var_name is upper of sanitized python variable name, so can be empty or duplicated.
        Priority:
        1) original name
        2) upper of original name
        3) unique upper of sanitized name
        4) upper of sanitized name + index
        """
        enum_option_key_map = {}
        if not self.enum:
            return enum_option_key_map

        # initialize value counter and sanitized_option_dict
        value_counter = defaultdict(int)
        sanitized_option_dict = {option: _sanitize_python_variable_name(option).upper() for option in self.enum}
        for option, sanitized_option in sanitized_option_dict.items():
            if len(sanitized_option) == 0:
                sanitized_option_dict[option] = "NO_NAME"
            value_counter[sanitized_option] += 1

        # deduplicate and keep the original order
        option_pairs, option_set = [], set()
        for option in self.enum:
            if option not in option_set:
                option_set.add(option)
                option_pairs.append((option, sanitized_option_dict[option]))

        # 1) original name
        option_pairs = self.update_name_for_options(
            option_pairs, lambda _option, _sanitized_option: _option == _sanitized_option, enum_option_key_map
        )

        # 2) upper of original name
        option_pairs = self.update_name_for_options(
            option_pairs, lambda _option, _sanitized_option: _option.upper() == _sanitized_option, enum_option_key_map
        )

        # 3) unique upper of sanitized name
        option_pairs = self.update_name_for_options(
            option_pairs, lambda _option, _sanitized_option: value_counter[_sanitized_option] == 1, enum_option_key_map
        )

        # 4) upper of sanitized name + index
        value_counter.clear()
        for option, _ in option_pairs:
            while True:
                sanitized_option = sanitized_option_dict[option]
                new_key = f"{sanitized_option}_{value_counter[sanitized_option]}"
                value_counter[sanitized_option] += 1
                if new_key not in enum_option_key_map:
                    enum_option_key_map[new_key] = option
                    break
        return enum_option_key_map

    def _get_enum_key(self, option):
        if option in self._enum_option_key_map.values():
            for key, val in self._enum_option_key_map.items():
                if val == option:
                    return key
        raise ValueError(f"Option {option} not found in enum {self.enum}")

    @property
    def var_2_options(self) -> dict:
        if self.enum:
            return self._enum_option_key_map
        return {}
