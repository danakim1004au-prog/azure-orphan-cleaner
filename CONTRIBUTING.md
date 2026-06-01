# Contributing to azure-orphan-cleaner

Thanks for your interest in improving `azure-orphan-cleaner`! This guide gets
you from a fresh clone to an open pull request.

## Development environment

Azure CLI extensions are developed with **azdev**, the official Azure CLI dev
tool.

```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/azure-orphan-cleaner.git
cd azure-orphan-cleaner

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install azdev and set up the CLI dev environment
pip install azdev
azdev setup --repo .             # or: azdev setup -c   (use installed CLI)

# 4. Register this extension locally
azdev extension add orphan_cleaner

# 5. Install the package in editable mode with dev extras
pip install -e ".[dev]"
```

Verify it loaded:

```bash
az orphan --help
```

## Code style

- **flake8** must pass: `flake8 azext_orphan_cleaner/`
- **Type hints are required** on every public function.
- Every public function needs a docstring (Google or reStructuredText style).
- Keep lines within 90 characters.

Run the full local check before pushing:

```bash
flake8 azext_orphan_cleaner/
pytest tests/unit/ --cov=azext_orphan_cleaner
```

## Pull-request checklist

- [ ] `flake8 azext_orphan_cleaner/` passes with no warnings.
- [ ] `pytest tests/unit/` passes and coverage did not drop.
- [ ] New behavior is covered by a unit test (Azure SDKs mocked).
- [ ] Public functions have type hints and docstrings.
- [ ] `CHANGELOG.md` has an entry under "Unreleased".
- [ ] PR description explains the *why*, not just the *what*.

## Adding a new orphan type (step by step)

Say you want to detect **orphaned snapshots**:

1. **Add a KQL query** in `custom.py` → `_KQL_QUERIES` under a new key, e.g.
   `"snapshot"`. Project at least `id, name, resourceGroup, location,
   subscriptionId, sku`.
2. **Add a cost estimate** in `_COST_TABLE` (and special-case it in
   `_estimate_cost` if it is size-based).
3. **Add the type** to `_VALID_TYPES` in `custom.py`.
4. **Add the deletion branch** in `_delete_targets()` using the right SDK
   client (e.g. `ComputeManagementClient.snapshots.begin_delete`).
5. **Register the choice** in `_params.py` → `RESOURCE_TYPES`.
6. **Document it** in the README support table and add an example to
   `_help.py`.
7. **Write a unit test** in `tests/unit/test_custom.py` mocking the new query
   and deletion call.

## Reporting an issue

Please include:

- **Command run** (with arguments, redact subscription IDs).
- **Expected vs. actual** behavior.
- **Environment**: `az version` output and `python --version`.
- **Logs**: re-run with `--debug` and paste the relevant excerpt.

Open issues at:
<https://github.com/danakim/azure-orphan-cleaner/issues>
