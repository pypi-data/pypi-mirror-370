"""
Decorators for AXL Workflows.

This module contains the @workflow and @step decorators for defining workflows.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol, TypedDict, TypeVar, cast, runtime_checkable

from ..ir import validate_step_args
from .workflow import Workflow

T = TypeVar("T", bound=type[Workflow])


class StepConfig(TypedDict, total=False):
    """Typed configuration attached to step functions at decoration time."""

    io_handler: str
    input_mode: str | dict[str, str]
    resources: dict[str, Any]
    retries: int
    env: dict[str, str]


@runtime_checkable
class StepFunction(Protocol):
    """Protocol for functions decorated with @step."""

    _is_step: bool
    _step_config: StepConfig
    _original_func: Callable[..., Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def workflow(
    *,
    name: str | None = None,
    image: str | None = None,
    io_handler: str | None = None,
) -> Callable[[T], T]:
    """
    Decorator for defining workflows with configuration overrides.

    Args:
        name: Workflow name (optional, defaults to class name)
        image: Docker image override
        io_handler: IO handler override

    Returns:
        Decorated workflow class

    Example:
        @workflow(name="my-workflow", image="custom:latest")
        class MyWorkflow(Workflow):
            def graph(self):
                return self.step1()
    """

    def decorator(cls: T) -> T:
        # Validate that the class inherits from Workflow
        if not issubclass(cls, Workflow):
            raise TypeError(f"Class {cls.__name__} must inherit from Workflow")

        # Store original __init__ method
        original_init = cls.__init__

        def new_init(self: Workflow, *args: Any, **kwargs: Any) -> None:
            # Apply decorator overrides to kwargs
            if image is not None:
                kwargs["image"] = image
            if io_handler is not None:
                kwargs["io_handler"] = io_handler

            # Call original __init__ with updated kwargs
            original_init(self, *args, **kwargs)

            # Set workflow name (prefer decorator override)
            self.name = name or cls.__name__

        # Replace the __init__ method
        cls.__init__ = new_init  # type: ignore[method-assign]

        # Add workflow metadata on the class (dynamic attrs by design)
        cls._is_workflow = True  # type: ignore[attr-defined]
        cls._workflow_name = name or cls.__name__  # type: ignore[attr-defined]

        return cls

    return decorator


def step(
    *,
    io_handler: str | None = None,
    input_mode: str | dict[str, str] | None = None,
    resources: dict[str, Any] | None = None,
    retries: int | None = None,
    env: dict[str, str] | None = None,
) -> Callable[[Callable[..., Any]], StepFunction]:
    """
    Decorator for defining workflow steps with configuration.

    Args:
        io_handler: IO handler override for this step
        input_mode: Input mode override ("object", "path", or {arg: mode})
        resources: Resource requirements (CPU, memory, etc.)
        retries: Number of retries for this step
        env: Environment variables for this step

    Returns:
        Decorated step function

    Example:
        @step(io_handler="parquet", retries=3)
        def preprocess(self, data):
            return processed_data
    """

    def decorator(func: Callable[..., Any]) -> StepFunction:
        # Build step configuration (only include provided keys)
        step_cfg: StepConfig = {}
        if io_handler is not None:
            step_cfg["io_handler"] = io_handler
        if input_mode is not None:
            step_cfg["input_mode"] = input_mode
        if resources is not None:
            step_cfg["resources"] = resources
        if retries is not None:
            step_cfg["retries"] = retries
        if env is not None:
            step_cfg["env"] = env

        # Attach attributes to the original function (ruff prefers direct assigns)
        cast(Any, func)._is_step = True
        cast(Any, func)._step_config = step_cfg

        # Create a wrapper that validates arguments
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Validate that all arguments are OutputRef instances
            validate_step_args(func.__name__, args, kwargs)
            # Call the original function
            return func(*args, **kwargs)

        # Copy attributes to wrapper so runtime can read them
        cast(Any, wrapper)._is_step = True
        cast(Any, wrapper)._step_config = step_cfg
        cast(Any, wrapper)._original_func = func

        # Explicit cast so mypy understands wrapper carries the attributes
        return cast(StepFunction, wrapper)

    return decorator
