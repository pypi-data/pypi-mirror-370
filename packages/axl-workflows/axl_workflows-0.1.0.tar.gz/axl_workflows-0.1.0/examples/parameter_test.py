"""
Example workflow demonstrating parameter passing.

This workflow shows how to use parameters passed via YAML file.
"""

from axl import Workflow, step, workflow


@workflow(name="parameter-test")
class ParameterTest(Workflow):
    """Test workflow that uses parameters."""

    @step()
    def process_data(self, data: str) -> str:
        """Process data using workflow parameters."""
        # Access parameters via self.workflow_params
        prefix = self.workflow_params.get("prefix", "default")
        suffix = self.workflow_params.get("suffix", "")
        return f"{prefix}_{data}{suffix}"

    @step()
    def generate_data(self) -> str:
        """Generate test data."""
        return "test_data"

    def graph(self):
        """Define the workflow graph."""
        data = self.generate_data()
        return self.process_data(data)


if __name__ == "__main__":
    # Test with parameters
    wf = ParameterTest(prefix="custom", suffix="_end")
    print("Workflow params:", wf.workflow_params)

    # This would be called by the CLI with parameters from YAML
    # uv run axl run local -m examples/parameter_test.py:ParameterTest --params params.yaml
