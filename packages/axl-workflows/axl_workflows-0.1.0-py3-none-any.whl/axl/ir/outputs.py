"""
Output references for AXL Workflows IR.

This module contains the OutputRef class for representing step outputs
during symbolic execution and IR building.
"""

from typing import Any


class OutputRef:
    """
    Reference to a step output for IR building.

    This class represents the output of a step during symbolic execution,
    allowing the IR builder to construct the workflow DAG without
    actually executing the steps.
    """

    def __init__(self, step_name: str, inputs: list["OutputRef"] | None = None) -> None:
        """
        Initialize an output reference.

        Args:
            step_name: Name of the step that produces this output
            inputs: List of input references this step depends on
        """
        self.step_name = step_name
        self.inputs = inputs or []
        self.metadata: dict[str, Any] = {}

    def __repr__(self) -> str:
        """String representation of the output reference."""
        return f"OutputRef({self.step_name})"

    def __str__(self) -> str:
        """String representation for user display."""
        return f"<output from {self.step_name}>"

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to this output reference.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata from this output reference.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def __call__(self, *args: Any, **kwargs: Any) -> "OutputRef":
        """
        Make OutputRef callable for symbolic execution.

        When called, returns self to allow chaining in symbolic mode.
        This enables syntax like: step2(step1()) where both return OutputRef.

        Args:
            *args: OutputRef arguments (inputs)
            **kwargs: Ignored in symbolic mode

        Returns:
            Self (for chaining)
        """
        # Update inputs with the arguments
        for arg in args:
            if isinstance(arg, OutputRef):
                if arg not in self.inputs:
                    self.inputs.append(arg)
        return self


def validate_step_args(func_name: str, args: tuple, kwargs: dict) -> None:
    """
    Validate that step arguments are OutputRef instances.

    Args:
        func_name: Name of the step function
        args: Positional arguments (excluding self)
        kwargs: Keyword arguments

    Raises:
        ValueError: If any argument is not an OutputRef
    """
    # Skip validation if no arguments (steps with no inputs are valid)
    if not args and not kwargs:
        return

    # Check positional arguments (skip first if it's self/cls)
    for i, arg in enumerate(args[1:], start=1):  # Skip self (first argument)
        if not isinstance(arg, OutputRef):
            raise ValueError(
                f"Step '{func_name}' argument {i} must be the result of another step. "
                f"Got {type(arg).__name__} instead of OutputRef. "
                f"Make sure you're passing the output of a previous step, not a regular Python object."
            )

    # Check keyword arguments
    for key, value in kwargs.items():
        if not isinstance(value, OutputRef):
            raise ValueError(
                f"Step '{func_name}' argument '{key}' must be the result of another step. "
                f"Got {type(value).__name__} instead of OutputRef. "
                f"Make sure you're passing the output of a previous step, not a regular Python object."
            )
