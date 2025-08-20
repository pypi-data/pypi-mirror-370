# 📌 AXL Workflows (axl) — Milestones & Tasks

---

## **M0 — Project Bootstrap (uv-native)**

**Goal:** Repo skeleton with uv, linting, CI, and minimal CLI.

**Tasks**

* [x] Init repo structure: `axl/`, `examples/`, `tests/`
* [x] Create `pyproject.toml` (PEP 621 metadata, uv config, dev deps)
* [x] Add `uv.lock` (committed)
* [x] Setup dev workflow: `uv venv`, `uv sync --dev`, `uv run …`
* [x] Pre-commit hooks: ruff, black, mypy
* [x] GitHub Actions: setup-uv, cache, run ruff + mypy + pytest
* [x] CLI stub: `axl --version` via Typer
* [x] Base README.md with quickstart (params-as-step, pickle default)

---

## **M1 — DSL & IR MVP**

**Goal:** Define workflows & inspect IR (with io metadata).

**Tasks**

* [x] Implement **`Workflow` base class** (defaults: image, default_io=pickle, input_mode_default, deps policy)
* [x] Implement **`@workflow` decorator** (attribute overrides)
* [x] Implement **`@step` decorator** with options:

  * `io_handler` (default to pickle)
  * `input_mode` = "object" | "path" | {arg: mode}
  * `resources`, `retries`, `env`
* [x] **Params-as-step pattern**: step calls inside `graph()` are symbolic (return `OutputRef`)
* [x] Parse workflow class → **IR** (`IRWorkflow`, `IRNode`, `IREdge`, **output IO metadata**: handler name, file ext)
* [x] Define **IOHandler protocol** + **`pickle_io_handler`** (save/load, metadata)
* [x] CLI: `axl validate -m myflow:MyWorkflow` (build IR; basic checks)
* [x] Unit tests for IR builder (nodes/edges, options captured)
* [x] Type-check CI (`uv run mypy axl`)

---

## **M1.5 — Local Runtime & Release**

**Goal:** Basic local execution and first PyPI release.

**Tasks**

* [x] **Local Runtime Engine**:
  * Implement `axl/runtime/local.py` with step execution
  * Topological sort and dependency resolution
  * Artifact management with IO handlers
  * Step method invocation and error handling
* [x] **CLI Execution**:
  * [x] `axl run local -m module:Class` command
  * [x] Workflow instantiation
  * [x] Parameter passing (`--params` YAML)
  * [x] Progress reporting and logging
* [x] **Runtime Tests**:
  * [x] End-to-end workflow execution tests
  * [x] Artifact save/load roundtrip tests
  * [x] Error handling and recovery tests
* [x] **Performance Improvements (completed)**:
  * [x] IR indexing for `get_node()` O(1) lookups
  * [x] Iterative IR traversal (builder) to avoid recursion limits
* [ ] **Release Preparation**:
  * Add PyPI metadata to `pyproject.toml` (name, version, license, classifiers)
  * `uv build && uv run twine check dist/*`
  * GitHub Actions: **tag-driven** release (OIDC trusted publisher)
  * README "Install / Quickstart"

➡️ **Release v0.1.0 (PyPI/TestPyPI)** 🎉

* **DSL & IR**: Workflow definition, step decorators, IR building
* **IO Handlers**: Pickle and cloudpickle serialization
* **Local Runtime**: Basic workflow execution
* **CLI**: Validation and local execution commands
* **First PyPI Release**: Installable package

---

## **M1.6 — Performance & UX Improvements**

**Goal:** Enhance performance and user experience with caching and better data handling.

**Tasks**

* [ ] **Workflow Hashing & Caching**:
  * Add `blake3` dependency for fast hashing
  * Implement `IRWorkflow.compute_hash()` method
  * Hash-based workflow identification and caching
  * CLI: show workflow hash for reproducibility
* [ ] **Hash-based Artifact Storage**:
  * LocalRuntime: optional `use_hash` flag
  * Store artifacts under `workspace/{hash}/` structure
  * Automatic cleanup of old workflow artifacts
  * Hash-based artifact lookup and organization
* [ ] **PyArrow/Parquet IO Handlers**:
  * Add `pyarrow` as optional dependency
  * Implement `ParquetIOHandler` for DataFrames
  * Implement `ArrowIOHandler` for Arrow tables
  * Automatic type detection and conversion
  * Performance benchmarks and tests

➡️ **Release v0.1.1**

* **Performance**: Workflow caching and hash-based storage
* **Data Handling**: PyArrow/Parquet support for ML workflows
* **User Experience**: Better artifact organization and reproducibility
* **Performance**: Faster data serialization and workflow execution

---

## **M2 — Argo Compiler**

**Goal:** Compile IR → Argo Workflow YAML (KFP-compatible).

**Tasks**

* [ ] Implement `compiler.argo`:

  * Templates/DAG
  * Map **outputs to artifact files** with proper extensions
  * Emit **IO manifest** (inputs/outputs with handler names/URIs)
  * Respect `resources`, `retries`, future `when`
* [ ] CLI: `axl compile --target argo --out out.yaml`
* [ ] Golden-file tests for YAML
* [ ] CI: run `argo lint` (if available)
* [ ] Example workflow (`examples/churn_workflow.py`)

➡️ **Release v0.2.0**

* **Argo Compiler**: IR → Argo Workflow YAML
* **KFP Compatibility**: Kubeflow Pipelines support
* **Artifact Management**: IO manifest generation
* **Production Ready**: Kubernetes deployment

---

## **M3 — Runner Container**

**Goal:** Execute steps with uv-powered envs and io_handlers.

**Tasks**

* [ ] `Dockerfile.runner`: install uv; cache at `/opt/uv-cache`
* [ ] Runner entrypoint (`axl.runtime.__main__`)

  * Parse IO manifest & step args
  * **Env setup**: create/reuse workflow venv (`uv sync` from lockfile/requirements)
  * **Inputs**: load via handler (`object`) or pass **paths** per `input_mode`
  * Invoke user function
  * **Outputs**: save via handler (default pickle); write metadata
* [ ] Artifact storage (PVC path; S3 later)
* [ ] Logging: structured JSON
* [ ] Local run: `axl run local -m module:Class`
* [ ] E2E tests: object↔path modes, pickle roundtrip, failures

➡️ **Release v0.3.0**

* **Runner Container**: Docker-based step execution
* **UV Integration**: Environment management with uv
* **Artifact Storage**: PVC and S3 support
* **Structured Logging**: JSON logs for observability
* **Production Execution**: Containerized workflow runs

---

## **M4 — Dagster Compiler**

**Goal:** Compile IR → Dagster ops & job for dev.

**Tasks**

* [ ] Implement `compiler.dagster` (ops, graph, job) that **invokes the runner** for uniform behavior
* [ ] CLI: `axl compile --target dagster --out dagster_job.py`
* [ ] Example job in `examples/`
* [ ] Golden tests for generated code

➡️ **Release v0.4.0**

* **Dagster Compiler**: IR → Dagster ops and jobs
* **Development Workflow**: Local Dagster execution
* **Uniform Behavior**: Same runner across backends
* **Developer Experience**: Rich Dagster UI integration

---

## **M5 — Dependency Management (uv-first) & Image Baking**

**Goal:** Reproducible deps at workflow level; optional warm env; baked images for prod.

**Tasks**

* [ ] Workflow-level deps:

  * `use_lockfile=True` (prefer `uv.lock`)
  * `requirements=[...]` **or** `requirements_file="requirements.txt"` fallback
* [ ] Optional **warm_env**: synthetic setup step to pre-build venv/cache
* [ ] CLI: `axl build-image -m module:Class --tag ghcr.io/you/axl:0.x`

  * Copy `pyproject.toml` + `uv.lock` / requirements
  * `uv sync --frozen` at build time (no runtime installs in prod)
* [ ] System packages only in baked images (no apt in runtime pods)
* [ ] Examples: pandas+sklearn workflow; large deps

➡️ **Release v0.5.0**

* **Dependency Management**: UV-first workflow deps
* **Image Baking**: Pre-built container images
* **Reproducible Builds**: Lockfile and frozen deps
* **Production Optimization**: No runtime installs
* **Large Dependency Support**: Efficient caching

---

## **M6 — UX & Extras**

**Goal:** Improve developer experience and observability.

**Tasks**

* [ ] `
