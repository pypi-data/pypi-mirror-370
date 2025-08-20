# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from ._base_compiler import BaseCompiler


class InternalComponentCompiler(BaseCompiler):
    """A compiler to compile v1.5 components"""

    def _update_compile_content(self):
        """Generate component dict and refine"""
        component_dict = self._component._to_dict()
        # for internal components, if code is absent in the spec yaml, we should regard it as "."
        if self.CODE_KEY not in component_dict or not component_dict[self.CODE_KEY]:
            component_dict[self.CODE_KEY] = "."
        # in the compiled yaml, code will always be set to value "."
        self._snapshot = self._get_component_snapshot(component_dict.pop(self.CODE_KEY, None))
        component_dict[self.CODE_KEY] = "."
        self._component_content = component_dict
