# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Argument definitions for the ``az sweeper`` command group."""

from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_three_state_flag,
)

RESOURCE_TYPES = ["disk", "nic", "publicip", "appserviceplan", "all"]


def load_arguments(self, _):
    """Declare arguments for ``sweeper scan`` and ``sweeper clean``."""

    with self.argument_context("sweeper scan") as c:
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            help="Limit the scan to a single resource group. "
                 "Defaults to the whole subscription.",
        )
        c.argument(
            "subscription_id",
            options_list=["--subscription-id"],
            help="Subscription to scan. Defaults to the active CLI subscription.",
        )
        c.argument(
            "resource_type",
            options_list=["--type"],
            arg_type=get_enum_type(RESOURCE_TYPES),
            default="all",
            help="Type of stale or unused resource to detect.",
        )
        c.argument(
            "estimate_cost",
            options_list=["--estimate-cost"],
            arg_type=get_three_state_flag(),
            help="Include an estimated monthly cost (USD) for each resource.",
        )

    with self.argument_context("sweeper clean") as c:
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            help="Limit deletion to a single resource group.",
        )
        c.argument(
            "subscription_id",
            options_list=["--subscription-id"],
            help="Subscription to operate on. Defaults to the active subscription.",
        )
        c.argument(
            "resource_type",
            options_list=["--type"],
            arg_type=get_enum_type(RESOURCE_TYPES),
            default="all",
            help="Type of stale or unused resource to delete.",
        )
        c.argument(
            "dry_run",
            options_list=["--dry-run"],
            arg_type=get_three_state_flag(),
            default=True,
            help="Preview deletions without removing anything (default: true). "
                 "Pass '--dry-run false' to delete for real.",
        )
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            action="store_true",
            help="Do not prompt for confirmation before deleting.",
        )
