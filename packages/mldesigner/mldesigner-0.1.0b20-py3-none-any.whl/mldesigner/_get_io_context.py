# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import typing

from mldesigner._exceptions import UserErrorException
from mldesigner._input_output import Output


class OutputContext:
    """Component outputs context, output can be accessed with `.<name>`."""

    def __init__(self):
        self._outputs: typing.Dict[str, Output] = dict()

    def __setattr__(self, name: str, value: str):
        if name == "_outputs":
            super(OutputContext, self).__setattr__(name, value)
        else:
            # note: we cannot know the Output type now, so specify `string` here;
            #       and we cannot validate value type, neither.
            self._outputs[name] = Output(type="string", early_available=True)
            # update name and value for later writing run history
            self._outputs[name]._port_name = name
            self._outputs[name]._value = value  # pylint: disable=protected-access
            self._outputs[name]._ready = False  # pylint: disable=protected-access

    def __getattr__(self, name: str) -> Output:
        if name == "_outputs":
            return super(OutputContext, self).__getattribute__(name)
        if name not in self._outputs.keys():
            error_message = f"Output {name!r} not found, please check the spelling of the name."
            raise UserErrorException(error_message)
        return self._outputs[name]


class IOContext:
    """Component IO context, includes outputs information
    and support operations on them (e.g. mark early available output ready).

    You can use `get_io_context` to get this during runtime.
    """

    def __init__(self):
        self._outputs = OutputContext()

    @property
    def outputs(self) -> OutputContext:
        return self._outputs


def get_io_context() -> IOContext:
    """Get `IOContext` that contains component outputs information during runtime.
    Outputs can be accessed via `.outputs` from `IOContext` object.
    Early available output can be marked as ready with below code.

    .. code-block:: python

                from mldesigner import get_io_context

                ctx = get_io_context()
                ctx.outputs.output = "meta.txt"
                ctx.outputs.output.ready()

                # multiple outputs to mark ready
                # omit the lines assign values
                ctx.outputs.output1.ready()
                ctx.outputs.output2.ready()

    """
    return IOContext()
