## Summary

<!-- What does this PR do and why? 1-3 bullet points. -->

-
-

## Type of change

- [ ] Bug fix
- [ ] New resource type detection
- [ ] Documentation update
- [ ] Refactor / cleanup
- [ ] CI/CD change

## New resource type checklist (skip if not applicable)

- [ ] KQL query added to `_KQL_QUERIES` in `custom.py`
- [ ] Cost estimate added to `_COST_TABLE`
- [ ] Type key added to `_VALID_TYPES`
- [ ] Deletion branch added to `_delete_targets()`
- [ ] Choice added to `RESOURCE_TYPES` in `_params.py`
- [ ] Help text / example updated in `_help.py`
- [ ] Unit test added (Azure SDK mocked)
- [ ] README support table updated

## General checklist

- [ ] `flake8 azext_resource_sweeper/` passes with no warnings
- [ ] `pytest tests/unit/` passes
- [ ] Type hints and docstrings added to all public functions
- [ ] `CHANGELOG.md` updated under `[Unreleased]`

## Test evidence

<!-- Paste the pytest output or a screenshot of CI passing -->

```
pytest tests/unit/ -v
```
