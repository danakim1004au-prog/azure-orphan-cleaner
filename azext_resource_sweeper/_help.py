# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Help text shown by ``az sweeper --help`` and the per-command help pages."""

from knack.help_files import helps

helps["sweeper"] = """
    type: group
    short-summary: Detect and safely clean up stale and unused Azure resources.
    long-summary: >
        Stale and unused resources (unattached disks, dangling NICs, unused public IPs,
        empty App Service plans) silently accumulate cost. This extension finds
        them via Azure Resource Graph and removes them safely.
"""

helps["sweeper scan"] = """
    type: command
    short-summary: Detect stale and unused resources across a subscription.

    examples:
        - name: Scan the entire subscription for every resource type.
          text: az sweeper scan
        - name: Scan only for unattached disks and show estimated monthly cost.
          text: az sweeper scan --type disk --estimate-cost
        - name: Scan a single resource group and output as JSON.
          text: az sweeper scan -g my-rg --type all --output json
"""

helps["sweeper clean"] = """
    type: command
    short-summary: Delete stale and unused resources (dry-run by default).
    long-summary: >
        Runs a scan and then deletes the matching resources. For safety the
        command runs in dry-run mode unless you pass '--dry-run false'.
    examples:
        - name: Preview what would be deleted (no changes made).
          text: az sweeper clean --type disk
        - name: Actually delete unused public IPs after confirming.
          text: az sweeper clean --type publicip --dry-run false
        - name: Delete all stale resources in a resource group without prompting.
          text: az sweeper clean -g my-rg --type all --dry-run false --yes
"""
