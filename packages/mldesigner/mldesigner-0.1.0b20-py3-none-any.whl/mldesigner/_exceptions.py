# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from mldesigner._constants import ErrorCategory


class SystemErrorException(Exception):
    """Exception when a system error occurs."""

    def __init__(self, message):
        self._error_category = ErrorCategory.SYSTEM_ERROR
        super().__init__(message)


class UserErrorException(Exception):
    """Exception when a general user error occurs."""

    def __init__(self, message):
        self._error_category = ErrorCategory.USER_ERROR
        super().__init__(message)


class ComponentDefiningError(UserErrorException):
    """This error indicates that the user define a mldesigner.command_component in an incorrect way."""

    def __init__(self, name, cause):
        """Init the error with the cause which causes the wrong mldesigner.command_component."""
        msg = f"Defining component '{name}' failed: {cause}."
        super().__init__(message=msg)


class NoComponentError(UserErrorException):
    """Exception when no valid mldesigner component found in specific file."""

    def __init__(self, file, name=None):
        """Error message inits here."""
        if name:
            msg = "No mldesigner.command_component with name {} found in {}."
            super().__init__(message=msg.format(name, file))
        else:
            msg = "No mldesigner.command_component found in {}."
            super().__init__(message=msg.format(file))


class RequiredComponentNameError(UserErrorException):
    """Exception when multiple mldesigner.command_components are found and no component name specified."""

    def __init__(self, file):
        """Error message inits here."""
        msg = "More than one mldesigner.command_component found in {}, '--name' parameter is required."
        super().__init__(message=msg.format(file))


class TooManyComponentsError(UserErrorException):
    """Exception when multiple mldesigner.command_components are found in single component entry."""

    def __init__(self, count, file, component_name=None):
        """Error message inits here."""
        if not component_name:
            msg = "Only one mldesigner.command_component is allowed per file, {} found in {}".format(count, file)
        else:
            msg = "More than one mldesigner.command_component with name %r found in %r, count %d." % (
                component_name,
                file,
                count,
            )
        super().__init__(message=msg)


class RequiredParamParsingError(UserErrorException):
    """This error indicates that a parameter is required but not exists in the command line."""

    def __init__(self, name):
        """Init the error with the parameter name and its arg string."""
        msg = "'{0}' cannot be None since it is not optional. Please make sure command option '{0}=xxx' exists."
        super().__init__(message=msg.format(name))


class ComponentExecutorDependencyException(UserErrorException):
    """
    This error indicates DependentComponentExecutor failed to use functions/entities from azure.ai.ml package,
    usually due to an update of said package that has breaking changes towards referred functions/entities.
    """


class MldesignerExecutionError(UserErrorException):
    """This error indicates mldesigner execute command failed."""

    def __init__(self, message):
        msg = f"Mldesigner execution failed: {message}"
        super().__init__(message=msg)


class ValidationException(Exception):
    """Exception when validation fails in mldesigner"""

    def __init__(self, message):
        self._error_category = ErrorCategory.USER_ERROR
        super().__init__(message)


class ImportException(Exception):
    """Exception when trying to import azure.ai.ml package in standalone mode"""

    def __init__(self, message):
        self._error_category = ErrorCategory.USER_ERROR
        super().__init__(message)


class ComponentException(Exception):
    """Exception when mldesigner fails to transform mldesigner input/output to azure.ai.ml input/output"""

    def __init__(self, message):
        self._error_category = ErrorCategory.USER_ERROR
        super().__init__(message)


class MldesignerCompileError(UserErrorException):
    """This error indicates mldesigner compile command failed."""

    def __init__(self, message):
        msg = f"Mldesigner compile failed: {message}"
        super().__init__(message=msg)


class UnexpectedKeywordError(UserErrorException):
    """Exception raised when an unexpected keyword parameter is provided in dynamic functions."""

    def __init__(self, func_name, keyword, keywords=None):
        message = "%s() got an unexpected keyword argument %r" % (func_name, keyword)
        message += ", valid keywords: %s." % ", ".join("%r" % key for key in keywords) if keywords else "."
        super().__init__(message=message)
