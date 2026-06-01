# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Help text shown by ``az orphan --help`` and the per-command help pages."""

from knack.help_files import helps

helps["orphan"] = """
    type: group
    short-summary: Detect and safely clean up orphaned Azure resources.
    long-summary: >
        Orphaned resources (unattached disks, dangling NICs, unused public IPs,
        empty App Service plans) silently accumulate cost. This extension finds
        them via Azure Resource Graph and removes them safely.
"""

helps["orphan scan"] = """
    type: command
    short-summary: Detect orphaned resources across a subscription or resource group.
    examples:
        - name: Scan the entire subscription for every orphan type.
          text: az orphan scan
        - name: Scan only for unattached disks and show estimated monthly cost.
          text: az orphan scan --type disk --estimate-cost
        - name: Scan a single resource group and output as JSON using the built-in --output flag.
          text: az orphan scan -g my-rg --type all --output json
"""

helps["orphan clean"] = """
    type: command
    short-summary: Delete orphaned resources (dry-run by default).
    long-summary: >
        Runs a scan and then deletes the matching resources. For safety the
        command runs in dry-run mode unless you pass '--dry-run false'.
    examples:
        - name: Preview what would be deleted (no changes made).
          text: az orphan clean --type disk
        - name: Actually delete orphaned public IPs after confirming.
          text: az orphan clean --type publicip --dry-run false
        - name: Delete all orphans in a resource group without prompting.
          text: az orphan clean -g my-rg --type all --dry-run false --yes
"""
