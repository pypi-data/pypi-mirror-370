"""
Iris KNN example workflow executed locally with LocalRuntime.

Run without modifying project dependencies:
  uv run --with scikit-learn python examples/iris_example.py
"""

from typing import Any

from axl import LocalRuntime, Workflow, step, workflow
from axl.ir import build_ir


@workflow(name="iris-knn")
class IrisKNN(Workflow):
    @step()
    def load_data(self) -> tuple[Any, Any]:
        from sklearn.datasets import load_iris

        data = load_iris()
        return data.data, data.target

    @step()
    def split(self, data: tuple[Any, Any]) -> tuple[Any, Any, Any, Any]:
        from sklearn.model_selection import train_test_split

        X, y = data
        return train_test_split(X, y, test_size=0.2, random_state=42)

    @step()
    def train(self, split_data: tuple[Any, Any, Any, Any]) -> tuple[Any, Any, Any]:
        from sklearn.neighbors import KNeighborsClassifier

        X_train, X_test, y_train, y_test = split_data
        clf = KNeighborsClassifier(n_neighbors=3)
        clf.fit(X_train, y_train)
        return clf, X_test, y_test

    @step()
    def evaluate(self, trained: tuple[Any, Any, Any]) -> float:
        from sklearn.metrics import accuracy_score

        clf, X_test, y_test = trained
        y_pred = clf.predict(X_test)
        return float(accuracy_score(y_test, y_pred))

    def graph(self):  # type: ignore[override]
        return self.evaluate(self.train(self.split(self.load_data())))


if __name__ == "__main__":
    ir = build_ir(IrisKNN)
    runtime = LocalRuntime(storage_backend="memory")
    result = runtime.execute_workflow(ir, IrisKNN())
    print(f"Accuracy: {result:.4f}")
