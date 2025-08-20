# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import Union

_DATA_PATH = Path(__file__).resolve().parent.parent / "data"
_COMPONENT_PATH = _DATA_PATH / "condition_output" / "component_spec.yaml"

# cspell:ignore rtype


def _condition_output(condition: Union[str, bool], *, input_a=None, input_b=None):
    """
    Create a dsl.condition_output node to link output to input_a or input_b depends on condition.

    Below is an example of using expression result to control which step is executed.
    If pipeline parameter 'int_param1' > 'int_param2', then 'input_a' will be linked as output,
    else, the 'input_b' will be linked.

    .. code-block:: python

        @pipeline
        def pipeline_func(int_param1: int, int_param2: int):
            step1 = component_func()
            step2 = another_component_func()
            condition_output_step = dsl.condition_output(
                condition=int_param1 > int_param2,
                input_a=true_step.outputs.output,
                input_b=false_step.outputs.output
            )
            # use 'step.outputs.output' to reference the output.
            post_process_component(
                input=condition_output_step.outputs.output
            )

    :param condition: The condition of the execution flow.
        The value could be a boolean type control output or a pipeline expression.
    :type condition: Union[str, bool, InputOutputBase]
    :param input_a: Output linked if condition resolved result is true.
    :type input_a: NodeOutput
    :param input_b: Output linked if condition resolved result is false.
    :type input_b: NodeOutput
    :return: The dsl.condition component.
    :rtype: azure.ai.ml.entities.Component
    """
    from mldesigner._azure_ai_ml import load_component

    condition_output_component_func = load_component(_COMPONENT_PATH)
    condition_node = condition_output_component_func(condition=condition, input_a=input_a, input_b=input_b)
    return condition_node
