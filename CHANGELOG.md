# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-01

### Added
- `az sweeper scan` to detect stale and unused resources via Azure Resource Graph.
- Detection for **unattached managed disks** (`--type disk`).
- Detection for **unused network interfaces** (`--type nic`).
- Detection for **unused public IP addresses** (`--type publicip`).
- Detection for **empty App Service plans** (`--type appserviceplan`).
- `--estimate-cost` option to report an estimated monthly USD cost per resource.
- `az sweeper clean` with a **dry-run-by-default** safety model
  (`--dry-run true`); requires `--dry-run false` plus confirmation (or `--yes`)
  to delete.
- GitHub Actions CI (flake8 + pytest matrix on Python 3.9 / 3.11 with coverage).
- GitHub Actions release pipeline that publishes to PyPI on `v*` tags.
- Issue templates (bug report, feature request) and PR template.
- `azure.cli.extensions` entry-point for full azdev compatibility.
- Apache 2.0 license.

[Unreleased]: https://github.com/danakim1004au-prog/azure-resource-sweeper/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/danakim1004au-prog/azure-resource-sweeper/releases/tag/v0.1.0
