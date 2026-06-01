# Contributing to azure-resource-sweeper

Thank you for helping improve `azure-resource-sweeper`!
This guide walks you from a fresh clone to an open pull request.

---

## Table of contents

1. [Development environment](#1-development-environment)
2. [Project structure](#2-project-structure)
3. [Code style](#3-code-style)
4. [Running tests](#4-running-tests)
5. [Pull-request checklist](#5-pull-request-checklist)
6. [Adding a new resource type](#6-adding-a-new-resource-type)
7. [Reporting an issue](#7-reporting-an-issue)

---

## 1. Development environment

This extension is developed with **azdev** — the official Azure CLI extension
development tool — and follows the `azext_` package convention required by the
Azure CLI extension loader.

```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/azure-resource-sweeper.git
cd azure-resource-sweeper

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install azdev
pip install azdev

# 4. Set up the CLI dev environment (links this repo to your local Azure CLI)
azdev setup --repo .

# 5. Register the extension with azdev
azdev extension add resource-sweeper

# 6. Verify the command group is recognised
az sweeper --help
```

If `azdev` setup fails (e.g., no Azure CLI installed), you can install in
editable mode directly:

```bash
pip install -e ".[dev]"
python -m build
az extension add --source dist/azure_resource_sweeper-*.whl
```

> **Why `azext_` prefix?**
> The Azure CLI extension loader discovers packages via the
> `azure.cli.extensions` entry-point group defined in `setup.py`.
> The package directory **must** start with `azext_` so the loader can
> find `COMMAND_LOADER_CLS` in `__init__.py`.

---

## 2. Project structure

```
azext_resource_sweeper/
├── __init__.py    # COMMAND_LOADER_CLS — CLI entry point
├── commands.py    # load_command_table — registers az sweeper scan / clean
├── custom.py      # scan_resources() / clean_resources() — core logic
├── _params.py     # load_arguments — CLI parameter definitions
└── _help.py       # Help text and usage examples
```

---

## 3. Code style

- **flake8** must pass: `flake8 azext_resource_sweeper/`
- **Type hints** are required on every public function.
- Every public function must have a **docstring** (Google style).
- Lines must be within **90 characters**.

Run before pushing:

```bash
flake8 azext_resource_sweeper/
pytest tests/unit/ -v
```

---

## 4. Running tests

```bash
# Unit tests only (no Azure subscription needed — all SDK calls are mocked)
pytest tests/unit/ -v

# With coverage report
pytest tests/unit/ -v --cov=azext_resource_sweeper --cov-report=term-missing

# Integration tests (requires AZURE_SUBSCRIPTION_ID env var)
export AZURE_SUBSCRIPTION_ID=<your-subscription-id>
pytest tests/integration/ -v
```

---

## 5. Pull-request checklist

- [ ] `flake8 azext_resource_sweeper/` passes with no warnings.
- [ ] `pytest tests/unit/` passes and coverage did not drop.
- [ ] New behavior is covered by a unit test (Azure SDKs mocked).
- [ ] Public functions have type hints and docstrings.
- [ ] `CHANGELOG.md` has an entry under `[Unreleased]`.
- [ ] PR description explains the *why*, not just the *what*.

---

## 6. Adding a new resource type

Example: adding detection for **unused Load Balancers**.

### Step 1 — Add a KQL query (`custom.py`)

```python
_KQL_QUERIES["loadbalancer"] = """
    Resources
    | where type =~ 'microsoft.network/loadbalancers'
    | where array_length(properties.backendAddressPools) == 0
    | project id, name, resourceGroup, location, subscriptionId,
              sku = tostring(sku.name)
"""
```

### Step 2 — Add a cost estimate (`custom.py`)

```python
_COST_TABLE["loadbalancer"] = 18.25  # Basic SKU flat per month
```

### Step 3 — Register the type (`custom.py`)

```python
_VALID_TYPES = (
    "disk", "nic", "publicip", "appserviceplan", "loadbalancer", "all"
)
```

### Step 4 — Add deletion logic (`custom.py` → `_delete_targets`)

```python
elif rtype == "loadbalancer":
    client = NetworkManagementClient(credential, sub)
    client.load_balancers.begin_delete(rg, name).result()
```

### Step 5 — Register the CLI choice (`_params.py`)

```python
RESOURCE_TYPES = [
    "disk", "nic", "publicip", "appserviceplan", "loadbalancer", "all"
]
```

### Step 6 — Add help text (`_help.py`)

Add an example under `helps["sweeper scan"]` and `helps["sweeper clean"]`.

### Step 7 — Write a unit test (`tests/unit/test_custom.py`)

Mock the Resource Graph query to return a fake Load Balancer row and assert
that `scan_resources()` returns it and `clean_resources()` calls the right
deletion API.

### Step 8 — Update documentation

Add a row to the **Supported resource types** table in `README.md` and a
`CHANGELOG.md` entry under `[Unreleased]`.

---

## 7. Reporting an issue

Use the GitHub issue templates:

- **Bug report** — unexpected error or wrong detection result
- **Feature request** — new resource type or capability

Open issues at:
<https://github.com/danakim1004au-prog/azure-resource-sweeper/issues>
