# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Integration tests that hit a real Azure subscription.

These are skipped automatically unless AZURE_SUBSCRIPTION_ID is set, so they
never break CI for contributors without Azure access. They run scan/clean in
read-only / dry-run mode only -- nothing is ever deleted.
"""

import os

import pytest

from azext_resource_sweeper import custom

SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID")

pytestmark = pytest.mark.skipif(
    not SUBSCRIPTION_ID,
    reason="AZURE_SUBSCRIPTION_ID not set; skipping live integration tests.",
)


class _RealCmd:
    """Lightweight command context backed by a real CLI profile."""

    def __init__(self):
        from azure.cli.core import get_default_cli

        self.cli_ctx = get_default_cli()


def test_scan_against_live_subscription():
    """A live scan returns a list and every row carries the expected keys."""
    cmd = _RealCmd()
    results = custom.scan_resources(
        cmd,
        subscription_id=SUBSCRIPTION_ID,
        resource_type="all",
        estimate_cost=True,
    )

    assert isinstance(results, list)
    for row in results:
        assert {"id", "name", "resourceGroup", "type"} <= set(row)
        assert "estimatedMonthlyCost" in row


def test_clean_dry_run_is_non_destructive():
    """clean() in dry-run mode must only ever report 'would-delete'."""
    cmd = _RealCmd()
    results = custom.clean_resources(
        cmd,
        subscription_id=SUBSCRIPTION_ID,
        resource_type="all",
        dry_run=True,  # hard-coded: never delete during integration tests
    )

    assert all(r["status"] == "would-delete" for r in results)
