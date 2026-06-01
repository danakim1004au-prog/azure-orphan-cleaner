# azure-orphan-cleaner

[![CI](https://github.com/danakim1004au-prog/azure-orphan-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/danakim1004au-prog/azure-orphan-cleaner/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/azure-orphan-cleaner.svg)](https://pypi.org/project/azure-orphan-cleaner/)
[![Python versions](https://img.shields.io/pypi/pyversions/azure-orphan-cleaner.svg)](https://pypi.org/project/azure-orphan-cleaner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An **Azure CLI extension** that detects and safely cleans up *orphaned
resources* — unattached disks, dangling NICs, unused public IPs and empty
App Service plans that quietly keep costing money.

## Why?

Orphaned resources are easy to create and easy to forget. They never show up
on a dashboard you look at, but they show up on the bill. `azure-orphan-cleaner`
uses **Azure Resource Graph** to find them in seconds and removes them with a
dry-run-first safety model.

## Installation

```bash
# As an Azure CLI extension (recommended)
az extension add --source azure_orphan_cleaner-0.1.0-py3-none-any.whl

# Or install the package directly from PyPI
pip install azure-orphan-cleaner
```

## Quick start

```bash
# 1. Find every orphaned resource in the active subscription
az orphan scan

# 2. Look for unattached disks and show what they cost each month
az orphan scan --type disk --estimate-cost

# 3. Scan one resource group and get JSON for scripting
az orphan scan -g my-rg --output json

# 4. Preview a cleanup (nothing is deleted — dry-run is the default)
az orphan clean --type publicip

# 5. Actually delete the orphans, skipping the prompt
az orphan clean --type all --dry-run false --yes
```

## Supported orphan types

| Type             | `--type` value   | Detection condition                       | Typical monthly cost |
|------------------|------------------|-------------------------------------------|----------------------|
| Unattached disk  | `disk`           | `properties.diskState == 'Unattached'`    | ~$0.05 / GB          |
| Orphaned NIC     | `nic`            | `isnull(properties.virtualMachine)`       | $0 (but blocks IP/VM)|
| Unused public IP | `publicip`       | `isnull(properties.ipConfiguration)`      | ~$3.65 (Standard)    |
| Empty App Service plan | `appserviceplan` | `properties.numberOfSites == 0`     | ~$54.75 (Basic B1)   |
| All of the above | `all` (default)  | —                                         | —                    |

## Command reference

### `az orphan scan`

| Option              | Default | Description                                          |
|---------------------|---------|------------------------------------------------------|
| `--resource-group`, `-g` | all RGs | Limit the scan to one resource group.           |
| `--subscription-id` | active  | Subscription to scan.                                |
| `--type`            | `all`   | `disk` / `nic` / `publicip` / `appserviceplan` / `all` |
| `--estimate-cost`   | off     | Add an `estimatedMonthlyCost` field to each row.     |
| `--output`, `-o`    | `table` | `table` / `json` / `tsv`.                            |

### `az orphan clean`

| Option              | Default | Description                                          |
|---------------------|---------|------------------------------------------------------|
| `--resource-group`, `-g` | all RGs | Limit deletion to one resource group.           |
| `--subscription-id` | active  | Subscription to operate on.                          |
| `--type`            | `all`   | Type of orphan to delete.                            |
| `--dry-run`         | `true`  | Preview only. Pass `--dry-run false` to delete.      |
| `--yes`, `-y`       | off     | Skip the confirmation prompt.                        |

## Authentication

Authentication uses `DefaultAzureCredential`, so once you have run
`az login` the extension just works. In CI you can use a service principal
(`AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_CLIENT_SECRET`) or a managed
identity — no extra configuration needed.

## Contributing

Contributions are very welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for how
to set up a local dev environment and add a new orphan detection type.

## License

[MIT](LICENSE) © Dana Kim
