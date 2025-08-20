"""
Example workflow: Customer Churn Prediction Training.

This demonstrates the intended AXL Workflows DSL syntax with params as a step
and io_handlers for object persistence.
"""

from pydantic import BaseModel

from axl import Workflow, step, workflow


# Parameters are just a normal step output (typed with Pydantic for convenience)
class TrainParams(BaseModel):
    seed: int = 42
    input_path: str = "data/raw.csv"


@workflow(name="churn-train", image="ghcr.io/you/axl-runner:0.1.0")
class ChurnTrain(Workflow):
    @step()
    def params(self) -> TrainParams:
        # Use defaults here; optionally read from YAML/env if you prefer
        return TrainParams()

    @step()  # default io_handler = pickle
    def preprocess(self, p: TrainParams):
        # TODO: Implement preprocessing logic
        # user code here - this would return a DataFrame or features object
        # persisted via pickle (default)
        return {"features": "preprocessed_data"}

    @step()
    def train(self, features, p: TrainParams):
        # TODO: Implement training logic
        # This would train a model and return it
        # persisted via pickle
        return {"model": "trained_model"}

    @step()
    def evaluate(self, model) -> float:
        # TODO: Implement evaluation logic
        return 0.9123

    def graph(self):
        p = self.params()
        feats = self.preprocess(p)
        model = self.train(feats, p)
        return self.evaluate(model)


if __name__ == "__main__":
    # TODO: Add CLI execution logic
    print("ChurnTrain workflow defined")
    print(
        "Use: axl compile -m churn_workflow.py:ChurnTrain --target argo --out churn.yaml"
    )
