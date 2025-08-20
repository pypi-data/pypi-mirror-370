# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
from typing import Union


class CommandLineArgument:
    """This class is used to generate command line arguments for an input/output in a component."""

    def __init__(self, param: Union["Input", "Output"], arg_name=None, arg_string=None):
        self._param = param
        self._arg_name = arg_name
        self._arg_string = arg_string

    @property
    def param(self) -> Union["Input", "Output"]:
        """Return the bind input/output/parameter"""
        return self._param

    @property
    def arg_string(self):
        """Return the argument string of the parameter."""
        return self._arg_string

    @property
    def arg_name(self):
        """Return the argument name of the parameter."""
        return self._arg_name

    @arg_name.setter
    def arg_name(self, value):
        self._arg_name = value

    def to_cli_option_str(self, style=None):
        """Return the cli option str with style, by default return underscore style --a_b."""
        return self.arg_string.replace("_", "-") if style == "hyphen" else self.arg_string

    def arg_group_str(self):
        """Return the argument group string of the input/output/parameter."""
        s = "%s=%s" % (self.arg_string, self._arg_placeholder())
        return "$[[%s]]" % s if type(self.param).__name__ == "Input" and self.param.optional else s

    def _arg_placeholder(self) -> str:
        raise NotImplementedError()


class MldesignerCommandLineArgument(CommandLineArgument):
    """This class is used to generate command line arguments for an input/output in a mldesigner.command_component."""

    def add_to_arg_parser(self, parser: argparse.ArgumentParser, default=None):
        """Add this parameter to ArgumentParser, both command line styles are added."""
        cli_str_underscore = self.to_cli_option_str(style="underscore")
        cli_str_hyphen = self.to_cli_option_str(style="hyphen")
        if default is not None:
            return parser.add_argument(cli_str_underscore, cli_str_hyphen, default=default)

        return parser.add_argument(
            cli_str_underscore,
            cli_str_hyphen,
        )

    def _arg_placeholder(self) -> str:
        io_tag = "outputs" if type(self.param).__name__ == "Output" else "inputs"
        return "'${{%s.%s}}'" % (io_tag, self.arg_string)
