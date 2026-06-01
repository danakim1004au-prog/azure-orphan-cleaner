# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Unit tests for azext_orphan_cleaner.custom.

Every Azure SDK client is replaced with a Mock so the tests run offline and
never touch a real subscription.
"""

import unittest
from unittest import mock

import pytest
from knack.util import CLIError

from azext_orphan_cleaner import custom


def _fake_cmd():
    """Return a minimal stand-in for the Azure CLI command context."""
    cmd = mock.MagicMock()
    cmd.cli_ctx = mock.MagicMock()
    return cmd


def _disk_row(name="orphan-disk", size=128):
    return {
        "id": f"/subscriptions/sub-1/resourceGroups/rg/providers/"
              f"Microsoft.Compute/disks/{name}",
        "name": name,
        "resourceGroup": "rg",
        "location": "eastus",
        "subscriptionId": "sub-1",
        "sku": "Standard_LRS",
        "diskSizeGb": size,
        "type": "disk",
    }


class ScanOrphansTests(unittest.TestCase):
    @mock.patch.object(custom, "_resolve_subscriptions", return_value=["sub-1"])
    @mock.patch.object(custom, "_run_graph_query")
    def test_scan_returns_disk_list(self, mock_query, _mock_subs):
        """scan_orphans() returns the unattached disks reported by the graph."""
        mock_query.return_value = [_disk_row("disk-a"), _disk_row("disk-b")]

        result = custom.scan_orphans(_fake_cmd(), resource_type="disk")

        assert len(result) == 2
        assert {r["name"] for r in result} == {"disk-a", "disk-b"}
        assert all(r["type"] == "disk" for r in result)

    @mock.patch.object(custom, "_resolve_subscriptions", return_value=["sub-1"])
    @mock.patch.object(custom, "_run_graph_query", return_value=[])
    def test_scan_empty_result(self, _mock_query, _mock_subs):
        """An empty graph response yields an empty list, not an error."""
        result = custom.scan_orphans(_fake_cmd(), resource_type="disk")
        assert result == []

    @mock.patch.object(custom, "_resolve_subscriptions", return_value=["sub-1"])
    @mock.patch.object(custom, "_run_graph_query")
    def test_estimate_cost_added(self, mock_query, _mock_subs):
        """estimate_cost=True annotates each row with estimatedMonthlyCost."""
        mock_query.return_value = [_disk_row(size=100)]

        result = custom.scan_orphans(
            _fake_cmd(), resource_type="disk", estimate_cost=True
        )

        assert "estimatedMonthlyCost" in result[0]
        # 100 GB * $0.05/GB = $5.00
        assert result[0]["estimatedMonthlyCost"] == pytest.approx(5.0)

    def test_invalid_type_raises(self):
        """An unknown --type value is rejected with a CLIError."""
        with pytest.raises(CLIError):
            custom.scan_orphans(_fake_cmd(), resource_type="bogus")


class CleanOrphansTests(unittest.TestCase):
    @mock.patch.object(custom, "_delete_targets")
    @mock.patch.object(custom, "scan_orphans")
    def test_clean_dry_run_no_deletion(self, mock_scan, mock_delete):
        """dry_run=True must never call the deletion path."""
        mock_scan.return_value = [_disk_row()]

        result = custom.clean_orphans(_fake_cmd(), resource_type="disk", dry_run=True)

        mock_delete.assert_not_called()
        assert result[0]["status"] == "would-delete"

    @mock.patch.object(custom, "_delete_targets")
    @mock.patch.object(custom, "scan_orphans")
    @mock.patch("azext_orphan_cleaner.custom.prompt_y_n", return_value=False)
    def test_clean_requires_confirmation(self, mock_prompt, mock_scan, mock_delete):
        """dry_run=False + yes=False prompts; declining aborts the deletion."""
        mock_scan.return_value = [_disk_row()]

        with pytest.raises(CLIError):
            custom.clean_orphans(
                _fake_cmd(), resource_type="disk", dry_run=False, yes=False
            )

        mock_prompt.assert_called_once()
        mock_delete.assert_not_called()

    @mock.patch.object(custom, "_delete_targets")
    @mock.patch.object(custom, "scan_orphans")
    def test_clean_yes_skips_prompt_and_deletes(self, mock_scan, mock_delete):
        """yes=True with dry_run=False deletes without prompting."""
        mock_scan.return_value = [_disk_row()]
        mock_delete.return_value = [{"name": "orphan-disk", "status": "deleted"}]

        result = custom.clean_orphans(
            _fake_cmd(), resource_type="disk", dry_run=False, yes=True
        )

        mock_delete.assert_called_once()
        assert result[0]["status"] == "deleted"


if __name__ == "__main__":
    unittest.main()
