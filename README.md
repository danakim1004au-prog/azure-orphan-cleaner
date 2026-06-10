# azure-resource-sweeper

[![CI](https://github.com/danakim1004au-prog/azure-resource-sweeper/actions/workflows/ci.yml/badge.svg)](https://github.com/danakim1004au-prog/azure-resource-sweeper/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/azure-resource-sweeper.svg)](https://pypi.org/project/azure-resource-sweeper/)
[![Python versions](https://img.shields.io/pypi/pyversions/azure-resource-sweeper.svg)](https://pypi.org/project/azure-resource-sweeper/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An **Azure CLI extension** that detects and safely cleans up *stale and unused
resources* — unattached disks, dangling NICs, unused public IPs and empty
App Service plans that quietly keep costing money.

---

## Why?

Stale resources are easy to create and easy to forget. They never show up
on a dashboard you look at, but they always show up on the bill.
`azure-resource-sweeper` uses **Azure Resource Graph KQL queries** to find
them in seconds and removes them with a dry-run-first safety model.

---

## Installation

### As an Azure CLI extension (recommended)

```bash
# Install directly from PyPI
az extension add --name azure-resource-sweeper

# Or from a local wheel (for development)
pip install build
python -m build
az extension add --source dist/azure_resource_sweeper-*-py3-none-any.whl
```

### For local development with azdev

```bash
pip install azdev
azdev setup --repo .
azdev extension add resource-sweeper
az sweeper --help
```

---

## Quick start

```bash
# 1. Scan the entire subscription for every stale resource type
az sweeper scan

# 2. Scan for unattached disks and show estimated monthly cost
az sweeper scan --type disk --estimate-cost

# 3. Scan a single resource group and output JSON
az sweeper scan -g my-rg --output json

# 4. Preview what would be deleted (dry-run — nothing is removed)
az sweeper clean --type publicip

# 5. Delete all stale resources without a prompt
az sweeper clean --type all --dry-run false --yes
```

---

## Supported resource types

| Type | `--type` | Detection condition | Typical monthly cost |
|------|----------|---------------------|----------------------|
| Unattached managed disk | `disk` | `properties.diskState == 'Unattached'` | ~$0.05 / GB |
| Disconnected NIC | `nic` | `isnull(properties.virtualMachine)` | $0 (blocks IP/VM removal) |
| Unused public IP | `publicip` | `isnull(properties.ipConfiguration)` | ~$3.65 (Standard) |
| Empty App Service plan | `appserviceplan` | `properties.numberOfSites == 0` | ~$54.75 (Basic B1) |
| All of the above | `all` (default) | — | — |

---

## Command reference

### `az sweeper scan`

| Option | Default | Description |
|--------|---------|-------------|
| `--resource-group`, `-g` | all RGs | Limit the scan to one resource group. |
| `--subscription-id` | active | Subscription to scan. |
| `--type` | `all` | `disk` / `nic` / `publicip` / `appserviceplan` / `all` |
| `--estimate-cost` | off | Add an `estimatedMonthlyCost` (USD) field to each row. |

### `az sweeper clean`

| Option | Default | Description |
|--------|---------|-------------|
| `--resource-group`, `-g` | all RGs | Limit deletion to one resource group. |
| `--subscription-id` | active | Subscription to operate on. |
| `--type` | `all` | Type of stale resource to delete. |
| `--dry-run` | `true` | Preview only. Pass `--dry-run false` to delete for real. |
| `--yes`, `-y` | off | Skip the interactive confirmation prompt. |

---

## Authentication

Authentication uses `DefaultAzureCredential` — once you have run `az login`
the extension just works. In CI, set the standard Azure SDK environment
variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`) or
use a managed identity — no extra configuration needed.

---

## Extension architecture

This project follows the **official Azure CLI extension format**:

| Requirement | Implementation |
|-------------|---------------|
| `azext_` package prefix | `azext_resource_sweeper/` |
| `COMMAND_LOADER_CLS` in `__init__.py` | `ResourceSweeperCommandsLoader` |
| `azure.cli.extensions` entry-point | `setup.py` → `entry_points` |
| `load_command_table` + `load_arguments` | `commands.py` + `_params.py` |
| azdev compatible | `azdev extension add resource-sweeper` |

---

## Contributing

Contributions are very welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for
how to set up a local dev environment, run tests, and add a new resource type.

---

## License

[Apache 2.0](LICENSE) © Dana Kim
