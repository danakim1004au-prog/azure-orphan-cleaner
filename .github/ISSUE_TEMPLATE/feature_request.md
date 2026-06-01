---
name: Feature request
about: Suggest a new resource type to detect or a new capability
title: "[Feature] <short description>"
labels: enhancement
assignees: danakim1004au-prog
---

## What problem does this solve?

A clear description of the pain point. Example: "There is no way to detect unused
Load Balancers, so they silently accumulate cost."

## Proposed solution

Describe what you'd like to happen. If you have a KQL query in mind, paste it here:

```kql
Resources
| where type =~ 'microsoft.network/loadbalancers'
| where ...
```

## Resource type details (if applicable)

| Field | Value |
|-------|-------|
| Azure resource type | e.g. `microsoft.network/loadbalancers` |
| Detection condition | e.g. `isnull(properties.backendAddressPools)` |
| Estimated monthly cost | e.g. ~$18 for Basic SKU |
| Deletion SDK | e.g. `NetworkManagementClient.load_balancers.begin_delete` |

## Alternatives considered

Describe any alternative solutions or workarounds you've considered.

## Additional context

Add any other context, screenshots, or links to Azure documentation here.
