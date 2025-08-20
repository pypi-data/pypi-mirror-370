# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
import typing

from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow.schema import Schema


class PythonModuleRelPathStr(fields.Str):
    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        """Validate module path"""
        module_path = super()._deserialize(value, attr, data, **kwargs)
        # remove ending slash
        module_path = module_path.rstrip("/")
        if module_path.startswith("/"):
            raise ValidationError("Module path starts with '/' is not supported.")

        if "\\" in module_path:
            raise ValidationError("Module path contains '\\' is not supported, please use posix style path '/'.")
        module_parts = module_path.split("/")
        for module_name in module_parts:
            pattern = r"^[a-z_][a-z\d_]*$"
            if not re.match(pattern, module_name):
                raise ValidationError(
                    "Module name should only contain lower letter, number, underscore and start with a lower letter. "
                    f"Error module name: {module_name}, module path: {module_path}."
                )
        return module_path


class PackageAssetsSchema(Schema):
    components = fields.Dict(keys=PythonModuleRelPathStr(), values=fields.List(fields.Str()))
