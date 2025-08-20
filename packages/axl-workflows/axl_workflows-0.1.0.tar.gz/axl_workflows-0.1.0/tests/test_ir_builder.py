"""
Tests for IR builder functionality.
"""

import pytest

from axl.core import Workflow, step, workflow
from axl.ir import (
    IREdge,
    IRNode,
    IRWorkflow,
    build_ir,
    get_step_config,
    get_step_config_from_output_ref,
    get_workflow_info,
    validate_workflow,
)


class TestIRBuilder:
    """Test cases for IR builder functionality."""

    def test_build_ir_simple_workflow(self) -> None:
        """Test building IR from a simple workflow."""

        @workflow(name="test-workflow")
        class SimpleWorkflow(Workflow):
            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Build IR
        ir = build_ir(SimpleWorkflow)

        # Check basic properties
        assert ir.name == "test-workflow"
        assert ir.image == "ghcr.io/axl-workflows/runner:latest"
        assert ir.io_handler == "pickle"
        assert len(ir.nodes) == 2
        assert len(ir.edges) == 1

        # Check nodes
        step1_node = ir.get_node("step1")
        step2_node = ir.get_node("step2")
        assert step1_node is not None
        assert step2_node is not None
        assert step1_node.inputs == []
        assert step2_node.inputs == ["step1"]

        # Check edges
        edge = ir.edges[0]
        assert edge.source == "step1"
        assert edge.target == "step2"

    def test_build_ir_complex_workflow(self) -> None:
        """Test building IR from a complex workflow with multiple dependencies."""

        @workflow(name="complex-workflow")
        class ComplexWorkflow(Workflow):
            @step()
            def load_data(self):
                return "raw_data"

            @step()
            def preprocess(self, data):
                return "processed_data"

            @step()
            def train(self, data):
                return "model"

            @step()
            def evaluate(self, model, data):
                return "score"

            def graph(self):
                data = self.load_data()
                processed = self.preprocess(data)
                model = self.train(processed)
                return self.evaluate(model, processed)

        # Build IR
        ir = build_ir(ComplexWorkflow)

        # Check basic properties
        assert ir.name == "complex-workflow"
        assert len(ir.nodes) == 4
        assert len(ir.edges) == 4

        # Check nodes
        load_node = ir.get_node("load_data")
        preprocess_node = ir.get_node("preprocess")
        train_node = ir.get_node("train")
        evaluate_node = ir.get_node("evaluate")

        assert load_node.inputs == []
        assert preprocess_node.inputs == ["load_data"]
        assert train_node.inputs == ["preprocess"]
        assert evaluate_node.inputs == ["train", "preprocess"]

        # Check edges
        edge_sources = {edge.source for edge in ir.edges}
        edge_targets = {edge.target for edge in ir.edges}
        assert edge_sources == {"load_data", "preprocess", "train"}
        assert edge_targets == {"preprocess", "train", "evaluate"}

    def test_build_ir_with_step_config(self) -> None:
        """Test building IR with step configuration."""

        @workflow(name="config-workflow")
        class ConfigWorkflow(Workflow):
            @step(io_handler="parquet", retries=3, resources={"cpu": "2"})
            def step1(self):
                return "data"

            @step(io_handler="numpy", env={"DEBUG": "true"})
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Build IR
        ir = build_ir(ConfigWorkflow)

        # Check step configurations
        step1_node = ir.get_node("step1")
        step2_node = ir.get_node("step2")

        assert step1_node.get_io_handler() == "parquet"
        assert step1_node.get_retries() == 3
        assert step1_node.get_resources() == {"cpu": "2"}

        assert step2_node.get_io_handler() == "numpy"
        assert step2_node.get_env() == {"DEBUG": "true"}

    def test_build_ir_validation(self) -> None:
        """Test that IR validation works correctly."""

        @workflow(name="valid-workflow")
        class ValidWorkflow(Workflow):
            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Should not raise any exception
        ir = build_ir(ValidWorkflow)
        ir.validate()

    def test_get_workflow_info(self) -> None:
        """Test getting workflow information."""

        @workflow(name="info-workflow")
        class InfoWorkflow(Workflow):
            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Get workflow info
        info = get_workflow_info(InfoWorkflow)

        # Check info
        assert info["name"] == "info-workflow"
        assert info["image"] == "ghcr.io/axl-workflows/runner:latest"
        assert info["io_handler"] == "pickle"
        assert info["step_count"] == 2
        assert set(info["steps"]) == {"step1", "step2"}
        assert info["final_step"] == "step2"

    def test_validate_workflow(self) -> None:
        """Test workflow validation function."""

        @workflow(name="valid-workflow")
        class ValidWorkflow(Workflow):
            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Should not raise any exception
        validate_workflow(ValidWorkflow)

    def test_build_ir_invalid_graph_return(self) -> None:
        """Test that building IR fails with invalid graph return."""

        @workflow(name="invalid-workflow")
        class InvalidWorkflow(Workflow):
            @step()
            def step1(self):
                return "data"

            def graph(self):
                return "not_an_output_ref"  # Invalid return

        # Should raise ValueError
        with pytest.raises(ValueError, match="must return an OutputRef"):
            build_ir(InvalidWorkflow)

    def test_build_ir_missing_step(self) -> None:
        """Test that building IR fails with missing step."""

        @workflow(name="missing-step-workflow")
        class MissingStepWorkflow(Workflow):
            @step()
            def step1(self):
                return "data"

            def graph(self):
                # This will fail because step2 doesn't exist
                return self.step2(self.step1())

        # Should raise AttributeError when trying to access step2
        with pytest.raises(AttributeError):
            build_ir(MissingStepWorkflow)

    def test_ir_workflow_validation_cycles(self) -> None:
        """Test that IR validation detects cycles."""
        # Create a workflow with cycles manually
        ir = IRWorkflow(
            name="cyclic-workflow",
            image="test:latest",
            io_handler="pickle",
            nodes=[
                IRNode("step1", {}, inputs=["step2"]),
                IRNode("step2", {}, inputs=["step1"]),
            ],
            edges=[
                IREdge("step1", "step2"),
                IREdge("step2", "step1"),
            ],
        )

        # Should raise ValueError for cycles
        with pytest.raises(ValueError, match="contains cycles"):
            ir.validate()

    def test_ir_workflow_validation_orphaned_nodes(self) -> None:
        """Test that IR validation detects orphaned nodes."""
        # Create a workflow with orphaned nodes
        ir = IRWorkflow(
            name="orphaned-workflow",
            image="test:latest",
            io_handler="pickle",
            nodes=[
                IRNode("step1", {}),
                IRNode("step2", {}),  # Orphaned
            ],
            edges=[],  # No edges
        )

        # Should raise ValueError for orphaned nodes
        with pytest.raises(ValueError, match="orphaned nodes"):
            ir.validate()

    def test_ir_workflow_validation_missing_dependencies(self) -> None:
        """Test that IR validation detects missing dependencies."""
        # Create a workflow with missing dependencies
        ir = IRWorkflow(
            name="missing-deps-workflow",
            image="test:latest",
            io_handler="pickle",
            nodes=[
                IRNode("step1", {}),
            ],
            edges=[
                IREdge("step1", "missing_step"),  # Missing target
            ],
        )

        # Should raise ValueError for missing dependencies
        with pytest.raises(ValueError, match="missing dependencies"):
            ir.validate()

    def test_get_step_config_missing_step(self) -> None:
        """Test get_step_config with missing step."""

        @workflow(name="test-workflow")
        class TestWorkflow(Workflow):
            @step()
            def step1(self):
                return "step1_output"

            def graph(self):
                return self.step1()

        wf = TestWorkflow()

        # Test with missing step
        with pytest.raises(
            ValueError, match="Step 'nonexistent' not found in workflow"
        ):
            get_step_config(wf, "nonexistent")

    def test_get_step_config_from_output_ref_with_metadata(self) -> None:
        """Test get_step_config_from_output_ref when metadata contains step_config."""

        @workflow(name="test-workflow")
        class TestWorkflow(Workflow):
            @step(io_handler="cloudpickle")
            def step1(self):
                return "step1_output"

            def graph(self):
                return self.step1()

        wf = TestWorkflow()
        final_output = wf.graph()

        # The OutputRef should have step_config in metadata
        config = get_step_config_from_output_ref(final_output, wf)
        assert config["io_handler"] == "cloudpickle"

    def test_get_step_config_from_output_ref_fallback(self) -> None:
        """Test get_step_config_from_output_ref fallback to workflow method."""

        @workflow(name="test-workflow")
        class TestWorkflow(Workflow):
            @step()
            def step1(self):
                return "step1_output"

            def graph(self):
                return self.step1()

        wf = TestWorkflow()
        final_output = wf.graph()

        # Remove step_config from metadata to test fallback
        if "step_config" in final_output.metadata:
            del final_output.metadata["step_config"]

        config = get_step_config_from_output_ref(final_output, wf)
        assert config["io_handler"] == "pickle"  # default from workflow

    def test_validate_workflow_with_error(self) -> None:
        """Test validate_workflow when build_ir fails."""

        @workflow(name="test-workflow")
        class TestWorkflow(Workflow):
            @step()
            def step1(self):
                return "step1_output"

            def graph(self):
                # This will fail validation
                return "not_an_output_ref"

        with pytest.raises(ValueError, match="Workflow validation failed"):
            validate_workflow(TestWorkflow)

    def test_get_workflow_info_with_invalid_graph_return(self) -> None:
        """Test get_workflow_info with invalid graph return type."""

        @workflow(name="test-workflow")
        class TestWorkflow(Workflow):
            @step()
            def step1(self):
                return "step1_output"

            def graph(self):
                # This will fail because it doesn't return OutputRef
                return "not_an_output_ref"

        with pytest.raises(ValueError, match="must return an OutputRef"):
            get_workflow_info(TestWorkflow)
