# --------------------------------------------------------------------------
# Copyright (c) Dana Kim. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Core detection and cleanup logic for orphaned Azure resources.

This module talks to the Azure Resource Graph to *detect* orphaned resources
and to the per-service management SDKs (compute / network) to *delete* them.
Authentication is handled by :class:`azure.identity.DefaultAzureCredential`,
which transparently picks up the credentials already used by ``az login``.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from knack.prompting import prompt_y_n
from knack.util import CLIError

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# KQL queries (Azure Resource Graph). Each query returns id / name /
# resourceGroup / location plus a couple of fields needed for cost estimation.
# --------------------------------------------------------------------------- #
_KQL_QUERIES: Dict[str, str] = {
    "disk": """
        Resources
        | where type =~ 'microsoft.compute/disks'
        | where properties.diskState == 'Unattached'
        | project id, name, resourceGroup, location, subscriptionId,
                  sku = tostring(sku.name),
                  diskSizeGb = toint(properties.diskSizeGB)
    """,
    "nic": """
        Resources
        | where type =~ 'microsoft.network/networkinterfaces'
        | where isnull(properties.virtualMachine)
              and isnull(properties.privateEndpoint)
        | project id, name, resourceGroup, location, subscriptionId,
                  sku = 'standard'
    """,
    "publicip": """
        Resources
        | where type =~ 'microsoft.network/publicipaddresses'
        | where isnull(properties.ipConfiguration)
              and isnull(properties.natGateway)
        | project id, name, resourceGroup, location, subscriptionId,
                  sku = tostring(sku.name)
    """,
    "appserviceplan": """
        Resources
        | where type =~ 'microsoft.web/serverfarms'
        | where toint(properties.numberOfSites) == 0
        | project id, name, resourceGroup, location, subscriptionId,
                  sku = tostring(sku.name)
    """,
}

# Rough USD / month estimates. Real billing depends on region & SKU; these are
# deliberately conservative ballpark figures, good enough for a "wake-up call".
_COST_TABLE: Dict[str, float] = {
    "disk": 0.05,          # per GB-month for Standard HDD managed disk
    "nic": 0.0,            # NICs are free, but block IP/VM deletion
    "publicip": 3.65,      # Standard static public IP, flat per month
    "appserviceplan": 54.75,  # Basic B1 plan flat per month
}

_VALID_TYPES = ("disk", "nic", "publicip", "appserviceplan", "all")


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _get_credential():
    """Return a :class:`DefaultAzureCredential`.

    Imported lazily so that ``az orphan --help`` does not pay the import cost.
    """
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def _resolve_subscriptions(cmd, subscription_id: Optional[str]) -> List[str]:
    """Return the list of subscription IDs to query.

    Falls back to the subscription of the current CLI context when the caller
    does not pass ``--subscription``.
    """
    if subscription_id:
        return [subscription_id]
    from azure.cli.core.commands.client_factory import get_subscription_id

    return [get_subscription_id(cmd.cli_ctx)]


def _run_graph_query(query: str, subscriptions: List[str]) -> List[Dict[str, Any]]:
    """Execute a single KQL query against Azure Resource Graph.

    Handles server-side paging via the ``$skipToken`` continuation token and
    returns a flat list of row dictionaries.
    """
    from azure.mgmt.resourcegraph import ResourceGraphClient
    from azure.mgmt.resourcegraph.models import (
        QueryRequest,
        QueryRequestOptions,
    )

    client = ResourceGraphClient(_get_credential())
    rows: List[Dict[str, Any]] = []
    skip_token: Optional[str] = None

    while True:
        request = QueryRequest(
            subscriptions=subscriptions,
            query=query,
            options=QueryRequestOptions(skip_token=skip_token, top=1000),
        )
        response = client.resources(request)
        rows.extend(response.data or [])
        skip_token = getattr(response, "skip_token", None)
        if not skip_token:
            break

    return rows


def _estimate_cost(resource_type: str, row: Dict[str, Any]) -> float:
    """Return an estimated monthly USD cost for a single orphaned resource."""
    base = _COST_TABLE.get(resource_type, 0.0)
    if resource_type == "disk":
        return round(base * float(row.get("diskSizeGb") or 0), 2)
    return round(base, 2)


def _types_to_scan(resource_type: str) -> List[str]:
    """Expand the ``--type`` argument into the concrete query keys to run."""
    if resource_type not in _VALID_TYPES:
        raise CLIError(
            f"Invalid --type '{resource_type}'. "
            f"Choose from: {', '.join(_VALID_TYPES)}"
        )
    if resource_type == "all":
        return list(_KQL_QUERIES.keys())
    return [resource_type]


# --------------------------------------------------------------------------- #
# Public commands
# --------------------------------------------------------------------------- #
def scan_orphans(
    cmd,
    resource_group: Optional[str] = None,
    subscription_id: Optional[str] = None,
    resource_type: str = "all",
    estimate_cost: bool = False,
) -> List[Dict[str, Any]]:
    """Detect orphaned resources via Azure Resource Graph.

    Args:
        cmd: The Azure CLI command context (injected by the CLI framework).
        resource_group: Limit the scan to a single resource group. When
            ``None`` the whole subscription is scanned.
        subscription_id: Subscription to query. Defaults to the active CLI
            subscription.
        resource_type: One of ``disk``, ``nic``, ``publicip``,
            ``appserviceplan`` or ``all``.
        estimate_cost: When ``True`` each row is annotated with an
            ``estimatedMonthlyCost`` field (USD).

    Returns:
        A list of dictionaries, one per orphaned resource, each containing at
        least ``id``, ``name``, ``resourceGroup``, ``location`` and ``type``.
    """
    # Validate --type first so a bad value fails fast and clearly, before we
    # touch the network to resolve the subscription.
    scan_types = _types_to_scan(resource_type)
    subscriptions = _resolve_subscriptions(cmd, subscription_id)
    results: List[Dict[str, Any]] = []

    for rtype in scan_types:
        query = _KQL_QUERIES[rtype]
        if resource_group:
            query += f"\n| where resourceGroup =~ '{resource_group}'"

        logger.debug("Running Resource Graph query for type=%s", rtype)
        for row in _run_graph_query(query, subscriptions):
            row["type"] = rtype
            if estimate_cost:
                row["estimatedMonthlyCost"] = _estimate_cost(rtype, row)
            results.append(row)

    logger.info("Found %d orphaned resource(s)", len(results))
    return results


def clean_orphans(
    cmd,
    resource_group: Optional[str] = None,
    subscription_id: Optional[str] = None,
    resource_type: str = "all",
    dry_run: bool = True,
    yes: bool = False,
) -> List[Dict[str, Any]]:
    """Delete orphaned resources discovered by :func:`scan_orphans`.

    Args:
        cmd: The Azure CLI command context.
        resource_group: Limit deletion to a single resource group.
        subscription_id: Subscription to operate on. Defaults to the active
            CLI subscription.
        resource_type: Which orphan type(s) to delete.
        dry_run: When ``True`` (the default) nothing is deleted; the function
            only reports what *would* be removed. This is the safety default.
        yes: Skip the interactive confirmation prompt. Ignored when
            ``dry_run`` is ``True``.

    Returns:
        A list of result dictionaries, each with ``id``, ``name``, ``type``
        and a ``status`` field (``would-delete`` / ``deleted`` / ``failed``).
    """
    targets = scan_orphans(
        cmd,
        resource_group=resource_group,
        subscription_id=subscription_id,
        resource_type=resource_type,
    )

    if not targets:
        logger.warning("No orphaned resources found. Nothing to clean.")
        return []

    if dry_run:
        return [
            {"id": t["id"], "name": t["name"], "type": t["type"],
             "status": "would-delete"}
            for t in targets
        ]

    if not yes:
        names = "\n  ".join(f"{t['type']}: {t['name']}" for t in targets)
        message = (
            f"About to permanently delete {len(targets)} resource(s):\n  "
            f"{names}\nAre you sure?"
        )
        if not prompt_y_n(message):
            raise CLIError("Deletion cancelled by user.")

    return _delete_targets(cmd, targets)


def _delete_targets(cmd, targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Perform the actual deletions through the per-service management SDKs."""
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.network import NetworkManagementClient
    from azure.mgmt.web import WebSiteManagementClient

    credential = _get_credential()
    results: List[Dict[str, Any]] = []

    for target in targets:
        sub = target["subscriptionId"]
        rg = target["resourceGroup"]
        name = target["name"]
        rtype = target["type"]
        record = {"id": target["id"], "name": name, "type": rtype}

        try:
            if rtype == "disk":
                client = ComputeManagementClient(credential, sub)
                client.disks.begin_delete(rg, name).result()
            elif rtype == "nic":
                client = NetworkManagementClient(credential, sub)
                client.network_interfaces.begin_delete(rg, name).result()
            elif rtype == "publicip":
                client = NetworkManagementClient(credential, sub)
                client.public_ip_addresses.begin_delete(rg, name).result()
            elif rtype == "appserviceplan":
                client = WebSiteManagementClient(credential, sub)
                client.app_service_plans.delete(rg, name)
            else:  # pragma: no cover - guarded earlier by _types_to_scan
                raise CLIError(f"Unsupported resource type: {rtype}")

            record["status"] = "deleted"
            logger.info("Deleted %s '%s'", rtype, name)
        except Exception as exc:  # noqa: BLE001 - report, never crash the batch
            record["status"] = "failed"
            record["error"] = str(exc)
            logger.error("Failed to delete %s '%s': %s", rtype, name, exc)

        results.append(record)

    return results
