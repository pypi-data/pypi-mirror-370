"""
Tests for the core DSL components.
"""

import pytest

from axl.core import Workflow, step, workflow


class TestWorkflow:
    """Test cases for Workflow base class."""

    def test_workflow_creation(self) -> None:
        """Test that Workflow can be instantiated."""
        workflow = Workflow()
        assert workflow is not None
        assert workflow.image == "ghcr.io/axl-workflows/runner:latest"
        assert workflow.io_handler == "pickle"

    def test_workflow_graph_not_implemented(self) -> None:
        """Test that Workflow graph method raises NotImplementedError."""
        workflow = Workflow()
        with pytest.raises(NotImplementedError):
            workflow.graph()

    def test_workflow_custom_configuration(self) -> None:
        """Test that Workflow can be configured with custom values."""
        workflow = Workflow(
            image="custom-image:latest",
            io_handler="parquet",
        )
        assert workflow.image == "custom-image:latest"
        assert workflow.io_handler == "parquet"

    def test_workflow_validation_invalid_io_handler(self) -> None:
        """Test that Workflow validates io_handler."""
        with pytest.raises(ValueError, match="io_handler must be"):
            Workflow(io_handler="invalid")

    def test_workflow_configure_method(self) -> None:
        """Test that Workflow configure method works."""
        workflow = Workflow()
        workflow.configure(image="new-image:latest", io_handler="numpy")
        assert workflow.image == "new-image:latest"
        assert workflow.io_handler == "numpy"

    def test_workflow_configure_invalid_option(self) -> None:
        """Test that Workflow configure validates options."""
        workflow = Workflow()
        with pytest.raises(ValueError, match="Unknown configuration option"):
            workflow.configure(invalid_option="value")

    def test_workflow_get_config_methods(self) -> None:
        """Test that Workflow config getter methods work."""
        workflow = Workflow(
            io_handler="parquet",
        )

        workflow_config = workflow.get_workflow_config()
        assert workflow_config["image"] == "ghcr.io/axl-workflows/runner:latest"
        assert workflow_config["io_handler"] == "parquet"

    def test_workflow_repr(self) -> None:
        """Test that Workflow __repr__ method works."""
        workflow = Workflow()
        repr_str = repr(workflow)
        assert "Workflow(" in repr_str
        assert "image=" in repr_str
        assert "io_handler=" in repr_str


class TestDecorators:
    """Test cases for workflow and step decorators."""

    def test_workflow_decorator_basic(self) -> None:
        """Test that workflow decorator works with basic configuration."""

        @workflow()
        class TestWorkflow(Workflow):
            def graph(self):
                return "test"

        wf = TestWorkflow()
        assert wf.name == "TestWorkflow"
        assert hasattr(wf, "_is_workflow")
        assert wf._is_workflow is True

    def test_workflow_decorator_with_overrides(self) -> None:
        """Test that workflow decorator applies overrides correctly."""

        @workflow(
            name="custom-workflow", image="custom-image:latest", io_handler="parquet"
        )
        class TestWorkflow(Workflow):
            def graph(self):
                return "test"

        wf = TestWorkflow()
        assert wf.name == "custom-workflow"
        assert wf.image == "custom-image:latest"
        assert wf.io_handler == "parquet"

    def test_workflow_decorator_invalid_class(self) -> None:
        """Test that workflow decorator validates inheritance."""
        with pytest.raises(TypeError, match="must inherit from Workflow"):

            @workflow()
            class InvalidWorkflow:
                pass

    def test_step_decorator_basic(self) -> None:
        """Test that step decorator works with basic configuration."""

        @step()
        def test_step() -> None:
            pass

        assert hasattr(test_step, "_is_step")
        assert test_step._is_step is True
        assert hasattr(test_step, "_step_config")

    def test_step_decorator_with_config(self) -> None:
        """Test that step decorator stores configuration correctly."""

        @step(io_handler="parquet", retries=3, resources={"cpu": "2", "memory": "4Gi"})
        def test_step() -> None:
            pass

        config = test_step._step_config
        assert config["io_handler"] == "parquet"
        assert config["retries"] == 3
        assert config["resources"] == {"cpu": "2", "memory": "4Gi"}
