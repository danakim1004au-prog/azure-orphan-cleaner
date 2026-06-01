# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-01

### Added
- `az orphan scan` to detect orphaned resources via Azure Resource Graph.
- Detection for **unattached managed disks** (`--type disk`).
- Detection for **orphaned network interfaces** (`--type nic`).
- Detection for **unused public IP addresses** (`--type publicip`).
- Detection for **empty App Service plans** (`--type appserviceplan`).
- `--estimate-cost` option to report an estimated monthly USD cost per resource.
- `--output` option supporting `table`, `json` and `tsv`.
- `az orphan clean` with a **dry-run-by-default** safety model
  (`--dry-run true`); requires `--dry-run false` plus confirmation (or `--yes`)
  to delete.
- GitHub Actions CI (flake8 + pytest matrix on Python 3.9 / 3.11 with coverage).
- GitHub Actions release pipeline that publishes to PyPI on `v*` tags.

[Unreleased]: https://github.com/danakim/azure-orphan-cleaner/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/danakim/azure-orphan-cleaner/releases/tag/v0.1.0
