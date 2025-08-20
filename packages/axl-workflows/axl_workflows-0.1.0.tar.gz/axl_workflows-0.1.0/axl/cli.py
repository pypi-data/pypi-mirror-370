"""
CLI entry point for AXL Workflows.

This module provides the command-line interface for the axl tool.
"""

import importlib
import sys
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .ir import build_ir, get_workflow_info
from .runtime import LocalRuntime

app = typer.Typer(
    name="axl",
    help="AXL Workflows - Lightweight framework for building data and ML workflows",
    add_completion=False,
)
console = Console()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=lambda v: typer.echo(f"axl {__version__}") if v else None,
        is_eager=True,
    ),
) -> None:
    """
    AXL Workflows - Write once → run anywhere (Dagster locally or Kubeflow in production).
    """
    pass


@app.command()
def version() -> None:
    """Show version information."""
    console.print(Panel(f"AXL Workflows v{__version__}", title="Version"))


def load_parameters(params_file: str | None) -> dict[str, Any]:
    """
    Load parameters from YAML file.

    Args:
        params_file: Path to YAML parameters file

    Returns:
        Dictionary of parameters

    Raises:
        typer.Exit: If file not found or invalid YAML
    """
    if not params_file:
        return {}

    try:
        params_path = Path(params_file)
        if not params_path.exists():
            raise FileNotFoundError(f"Parameters file not found: {params_path}")

        with open(params_path) as f:
            params = yaml.safe_load(f)

        if not isinstance(params, dict):
            raise ValueError("Parameters file must contain a YAML dictionary")

        console.print(
            f"[green]Loaded {len(params)} parameters from {params_file}[/green]"
        )
        return params

    except Exception as e:
        console.print(f"[red]Error loading parameters: {e}[/red]")
        raise typer.Exit(1) from None


def load_workflow_class(module_path: str) -> type:
    """
    Load workflow class from module path.

    Args:
        module_path: Module path in format 'module:Class' or 'path/to/file.py:Class'

    Returns:
        Workflow class

    Raises:
        typer.Exit: If module or class not found
    """
    try:
        if ":" not in module_path:
            raise ValueError(
                "Module path must be in format 'module:Class' or 'path/to/file.py:Class'"
            )

        module_spec, class_name = module_path.split(":", 1)

        # Handle file paths
        if module_spec.endswith(".py"):
            file_path = Path(module_spec)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Add parent directory to sys.path
            sys.path.insert(0, str(file_path.parent))
            module_spec = file_path.stem

        # Import module
        module = importlib.import_module(module_spec)

        # Get class
        if not hasattr(module, class_name):
            raise AttributeError(
                f"Class '{class_name}' not found in module '{module_spec}'"
            )

        workflow_class = getattr(module, class_name)

        # Validate it's a workflow class
        if not hasattr(workflow_class, "_is_workflow"):
            raise ValueError(
                f"Class '{class_name}' is not a workflow class (missing @workflow decorator)"
            )

        return workflow_class  # type: ignore[no-any-return]

    except Exception as e:
        console.print(f"[red]Error loading workflow: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def validate(
    module: str = typer.Argument(
        ...,
        help="Module path to workflow class (e.g., 'myflow:MyWorkflow')",
    ),
) -> None:
    """Validate a workflow definition."""
    try:
        console.print(f"[yellow]Validating workflow: {module}[/yellow]")

        # Load workflow class
        workflow_class = load_workflow_class(module)

        # Get basic info
        info = get_workflow_info(workflow_class)

        # Display workflow info
        table = Table(title="Workflow Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", info["name"])
        table.add_row("Image", info["image"])
        table.add_row("IO Handler", info["io_handler"])
        table.add_row("Steps", str(info["step_count"]))

        console.print(table)

        # Validate workflow
        console.print("\n[yellow]Building IR and validating...[/yellow]")
        ir_workflow = build_ir(workflow_class)

        # Display validation results
        console.print("[green]✅ Workflow is valid![/green]")

        # Show step details
        step_table = Table(title="Steps")
        step_table.add_column("Step", style="cyan")
        step_table.add_column("Inputs", style="blue")
        step_table.add_column("IO Handler", style="green")

        for node in ir_workflow.nodes:
            inputs = ", ".join(node.inputs) if node.inputs else "None"
            io_handler = node.get_io_handler() or "default"
            step_table.add_row(node.name, inputs, io_handler)

        console.print(step_table)

    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def compile(
    module: str = typer.Argument(
        ...,
        help="Module path to workflow class (e.g., 'myflow:MyWorkflow')",
    ),
    target: str = typer.Option(
        "argo",
        "--target",
        "-t",
        help="Target backend (argo, dagster)",
    ),
    out: str = typer.Option(
        None,
        "--out",
        "-o",
        help="Output file path",
    ),
) -> None:
    """Compile a workflow to target backend."""
    # TODO: Implement workflow compilation
    console.print(f"[yellow]Compiling {module} to {target}[/yellow]")
    if out:
        console.print(f"[yellow]Output: {out}[/yellow]")
    console.print("[red]Not implemented yet[/red]")


@app.command()
def run(
    backend: str = typer.Argument(
        "local",
        help="Backend to run on (local, argo, dagster)",
    ),
    module: str = typer.Option(
        None,
        "--module",
        "-m",
        help="Module path to workflow class (e.g., 'examples/iris_example.py:IrisKNN')",
    ),
    storage_backend: str = typer.Option(
        "memory",
        "--storage",
        help="Storage backend for artifacts (memory|local)",
    ),
    workspace: str = typer.Option(
        "axl_workspace",
        "--workspace",
        help="Workspace directory for local storage backend",
    ),
    params: str = typer.Option(
        None,
        "--params",
        "-p",
        help="Parameters file (YAML) to pass to workflow constructor",
    ),
) -> None:
    """Run a workflow on the specified backend.

    Currently implemented: local backend using LocalRuntime.
    """
    try:
        console.print(f"[yellow]Running workflow on {backend}[/yellow]")

        if backend != "local":
            console.print("[red]Only 'local' backend is implemented for now[/red]")
            raise typer.Exit(1)

        if not module:
            console.print("[red]--module is required for local execution[/red]")
            raise typer.Exit(1)

        # Load parameters if provided
        workflow_params = load_parameters(params)

        # Load workflow class
        workflow_class = load_workflow_class(module)

        # Build IR
        ir_workflow = build_ir(workflow_class)

        # Instantiate workflow with parameters
        wf_instance = workflow_class(**workflow_params)

        # Execute locally
        console.print(
            f"[yellow]Executing locally (storage={storage_backend}, workspace='{workspace}')[/yellow]"
        )
        runtime = LocalRuntime(
            workspace_path=workspace, storage_backend=storage_backend
        )
        runtime.execute_workflow(ir_workflow, wf_instance)

        console.print(Panel("Local run completed", title="Run"))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Run failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def render(
    module: str = typer.Argument(
        ...,
        help="Module path to workflow class",
    ),
    out: str = typer.Option(
        None,
        "--out",
        "-o",
        help="Output file path (e.g., dag.png)",
    ),
) -> None:
    """Render workflow DAG as a graph."""
    # TODO: Implement DAG rendering
    console.print(f"[yellow]Rendering DAG for {module}[/yellow]")
    if out:
        console.print(f"[yellow]Output: {out}[/yellow]")
    console.print("[red]Not implemented yet[/red]")


if __name__ == "__main__":
    app()
