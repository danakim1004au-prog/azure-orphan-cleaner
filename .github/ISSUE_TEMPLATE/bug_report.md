---
name: Bug report
about: Report a bug or unexpected behavior in azure-resource-sweeper
title: "[Bug] <short description>"
labels: bug
assignees: danakim1004au-prog
---

## Describe the bug

A clear and concise description of what the bug is.

## Command used

```bash
az sweeper <verb> [options]
```

## Expected behavior

What you expected to happen.

## Actual behavior

What actually happened. Include the full error message or unexpected output.

## Environment

| Item | Value |
|------|-------|
| OS | e.g. Ubuntu 22.04 / macOS 14 |
| Python version | `python --version` |
| Azure CLI version | `az version` |
| Extension version | `az extension show -n azure-resource-sweeper` |

## Debug log

Re-run with `--debug` and paste the relevant excerpt:

```
az sweeper scan --debug 2>&1 | tail -50
```

## Additional context

Add any other context about the problem here (screenshots, subscription type, etc.).
