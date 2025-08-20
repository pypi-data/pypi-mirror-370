"""
Example workflow demonstrating logging functionality.

This workflow shows how to use self.log in workflow steps for custom logging.
"""

from typing import Any

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from axl import Workflow, step, workflow


@workflow(name="logging-demo")
class LoggingDemo(Workflow):
    """Demo workflow showing logging capabilities."""

    @step()
    def load_data(self) -> tuple[Any, Any]:
        """Load and log dataset information."""
        # User-defined logging
        self.log.info("Loading iris dataset")
        self.log.debug("Dataset has 150 samples, 4 features")

        data = load_iris()

        # Log custom information
        self.log.info(
            "Dataset loaded successfully",
            samples=len(data.data),
            features=data.data.shape[1],
            target_names=list(data.target_names),
        )

        return data.data, data.target

    @step()
    def split(self, data: tuple[Any, Any]) -> tuple[Any, Any, Any, Any]:
        """Split data and log split information."""
        X, y = data

        self.log.info(
            "Splitting dataset", total_samples=len(X), test_size=0.2, random_state=42
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.log.info(
            "Dataset split completed",
            train_samples=len(X_train),
            test_samples=len(X_test),
        )

        return X_train, X_test, y_train, y_test

    @step()
    def train(self, split: tuple[Any, Any, Any, Any]) -> tuple[Any, Any, Any]:
        """Train model and log training information."""
        X_train, X_test, y_train, y_test = split

        self.log.info(
            "Training KNN model",
            train_samples=len(X_train),
            test_samples=len(X_test),
            n_neighbors=3,
        )

        clf = KNeighborsClassifier(n_neighbors=3)
        clf.fit(X_train, y_train)

        self.log.info("Model training completed successfully")

        return clf, X_test, y_test

    @step()
    def evaluate(self, trained: tuple[Any, Any, Any]) -> float:
        """Evaluate model and log results."""
        clf, X_test, y_test = trained

        self.log.info("Evaluating model", test_samples=len(X_test))

        y_pred = clf.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))

        self.log.info(
            "Model evaluation completed",
            accuracy=f"{accuracy:.4f}",
            correct_predictions=int(accuracy * len(y_test)),
            total_predictions=len(y_test),
        )

        return accuracy

    def graph(self):
        """Define the workflow graph."""
        data = self.load_data()
        split_data = self.split(data)
        trained_model = self.train(split_data)
        return self.evaluate(trained_model)


if __name__ == "__main__":
    # This demonstrates how to run it locally using the Python API
    # For CLI execution, use: uv run axl run local -m examples/logging_example.py:LoggingDemo

    from axl.ir import build_ir
    from axl.runtime import LocalRuntime

    ir = build_ir(LoggingDemo)
    result = LocalRuntime(storage_backend="memory").execute_workflow(ir, LoggingDemo())
    print(f"\n🎯 Final accuracy: {result:.4f}")
