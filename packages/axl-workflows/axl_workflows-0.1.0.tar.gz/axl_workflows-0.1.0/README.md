# AXL Workflows (`axl`)

[![CI](https://github.com/axl-workflows/axl/actions/workflows/ci.yml/badge.svg)](https://github.com/axl-workflows/axl/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/axl-workflows.svg)](https://pypi.org/project/axl-workflows/)
[![Python](https://img.shields.io/pypi/pyversions/axl-workflows.svg)](https://pypi.org/project/axl-workflows/)

**AXL Workflows (axl)** is a lightweight framework for building **data and ML workflows** with a **class-based Python syntax**.
It compiles your workflows into:

* **Dagster jobs** → for **local development**, type checking, and fast iteration.
* **Argo Workflows YAML** → to run on **Kubeflow Pipelines** (KFP) in Kubernetes clusters.

**Write once → run anywhere (Dagster locally or Kubeflow in production).**

---

## 🚀 Quick Start

```bash
# Install
pip install axl-workflows

# Or with uv
uv pip install axl-workflows

# Create your first workflow
axl --help
```

---

## ✨ Key Features

* **Class-based DSL**: Define workflows as Python classes, with steps as methods and a `graph()` to wire them.
* **Simple params**: Treat parameters as a **normal step** that returns a Python object (e.g., a Pydantic model or dict). No special Param/Artifact classes.
* **IO Handlers**: Steps return **plain Python objects**; axl persists/loads them via an `io_handler` (default: **pickle**).

  * Per-step override (`@step(io_handler=...)`)
  * **Input modes**: receive **objects** by default or **file paths** with `input_mode="path"`.
* **Intermediate Representation (IR)**: Backend-agnostic DAG model (nodes, edges, resources, IO metadata).
* **Multiple backends**:

  * **Dagster** → ops/jobs/resources for local/dev runs.
  * **Argo/KFP** → YAML generation for production pipelines.
* **Unified runner image**: One container executes steps in both Dagster and Argo pods (uses **uv** for fast, reproducible envs).
* **Resource & retry hints**: Declare CPU, memory, caching, retries, and conditions at the step level.
* **CLI tools**: Compile, validate, run locally, or render DAGs.

---

## 📦 Example Workflow (params as a step, with Pydantic)

```python
# examples/churn_workflow.py
from axl import workflow, step
from pydantic import BaseModel

# Parameters are just a normal step output (typed with Pydantic for convenience).
class TrainParams(BaseModel):
    seed: int = 42
    input_path: str = "data/raw.csv"

@workflow(name="churn-train", image="ghcr.io/you/axl-runner:0.1.0")
class ChurnTrain:

    @step
    def params(self) -> TrainParams:
        # Use defaults here; optionally read from YAML/env if you prefer.
        return TrainParams()

    @step  # default io_handler = pickle
    def preprocess(self, p: TrainParams):
        import pandas as pd
        df = pd.read_csv(p.input_path)
        # ... feature engineering ...
        return df  # persisted via pickle (default)

    @step
    def train(self, features, p: TrainParams):
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        y = (features.sum(axis=1) > features.sum(axis=1).median()).astype(int)
        X = features.select_dtypes(include=[np.number]).fillna(0)
        model = RandomForestClassifier(n_estimators=50, random_state=p.seed).fit(X, y)
        return model  # persisted via pickle

    @step
    def evaluate(self, model) -> float:
        # pretend evaluation
        return 0.9123

    def graph(self):
        p = self.params()
        feats = self.preprocess(p)
        model = self.train(feats, p)
        return self.evaluate(model)
```

**Variations**

* Receive a **file path** instead of an object:

  ```python
  from pathlib import Path

  @step(input_mode={"features": "path"})
  def profile(self, features: Path) -> dict:
      return {"bytes": Path(features).stat().st_size}
  ```

* Override the **io handler** (e.g., Parquet for DataFrames):

  ```python
  from axl.io.parquet_io import parquet_io_handler

  @step(io_handler=parquet_io_handler)
  def preprocess(self, p: TrainParams):
      import pandas as pd
      return pd.read_csv(p.input_path)  # saved as .parquet; downstream gets a DataFrame
  ```

---

## 🛠 CLI

```bash
# Compile to Argo YAML
axl compile -m examples/churn_workflow.py:ChurnTrain --target argo --out churn.yaml

# Compile to Dagster job (Python module output)
axl compile -m examples/churn_workflow.py:ChurnTrain --target dagster --out dagster_job.py

# Run locally
axl run local -m examples/churn_workflow.py:ChurnTrain

# (Optional) Provide params to your own params() step via file/env if you implement that logic
# axl run local -m examples/churn_workflow.py:ChurnTrain --params params.yaml

# Validate workflow definition
axl validate -m examples/churn_workflow.py:ChurnTrain

# Render DAG graph
axl render -m examples/churn_workflow.py:ChurnTrain --out dag.png
```

---

## 📐 Architecture

1. **Authoring Layer**

   * Python DSL: `@workflow`, `@step`
   * **Params are a normal step** (often a Pydantic model)
   * IO handled by **io\_handlers** (default: pickle)
   * Wire dependencies via `graph()`

2. **IR (Intermediate Representation)**

   * Abstract DAG: nodes, edges, inputs/outputs, resources, retry policies, IO metadata

3. **Compilers**

   * **DagsterBackend**: generates ops, jobs, resources for dev
   * **ArgoBackend**: generates Argo Workflow YAML (KFP-compatible)

4. **Runtime**

   * Unified runner image (`axl-runner`) executes steps
   * Handles env (via **uv**), IO handler save/load, logging, retries

5. **CLI**

   * Single interface for compile, run, validate, render

---

## 📂 Project Structure

```
axl/
  core/          # DSL: decorators, base classes, typing
  io/            # io_handlers (pickle default; parquet/npy/torch optional)
  ir/            # Intermediate Representation (nodes, edges, workflows)
  compiler/      # Backend compilers (Argo, Dagster)
  runtime/       # Runner container + IO + env setup (uv)
  cli.py         # CLI entrypoint
examples/
  churn_workflow.py
tests/
  test_core.py   # Tests for DSL components
  test_ir.py     # Tests for IR components
pyproject.toml
README.md
```

---

## 🚀 Roadmap

* **v0.1 (MVP)**

  * DSL for workflows & steps
  * IR builder
  * Argo compiler (PVC artifacts, retries, resources)
  * Runner container (PVC support)
  * CLI: compile, run local

* **v0.2**

  * Dagster compiler (ops/jobs)
  * S3/MinIO artifact support
  * Simple caching
  * Graph rendering

* **v0.3**

  * Conditional execution (`when`)
  * Metrics export (Prometheus, Argo/KFP UI)
  * KFP-specific features (experiments, parameters UI)

---

## 🎯 Why AXL Workflows?

* **Dagster is great for dev** but doesn’t natively compile to Argo/KFP.
* **Kubeflow Pipelines is production-grade** but YAML is verbose and hard to maintain.
* **axl bridges the gap**:

  * Simple, class-based DSL
  * **Params as a normal step** (optional Pydantic)
  * IO handlers for painless object ↔ file persistence
  * Backend-agnostic IR
  * Compile once, run anywhere
