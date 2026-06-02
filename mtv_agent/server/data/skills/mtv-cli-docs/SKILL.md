---
name: mtv-cli-docs
description: Find kubectl-mtv CLI documentation links and usage guidance. Use when the user asks about kubectl-mtv commands, CLI migration workflows, TSL query syntax, KARL affinity rules, provider setup via CLI, inventory queries, plan creation flags, or any kubectl-mtv technical guide topic.
---

# kubectl-mtv CLI Technical Guide

Use this TOC to suggest the most relevant documentation link when a user asks about kubectl-mtv CLI topics.
Always link to the specific chapter page. Base URL: `https://yaacov.github.io/kubectl-mtv/guide/`

## Getting Command Help

For detailed flags, syntax, and examples of any `kubectl-mtv` command, use the MTV MCP `mtv_help` tool:

```
mtv_help("<command>")
```

Examples:
- `mtv_help("create plan")` — all flags and examples for plan creation
- `mtv_help("get inventory")` — inventory query syntax and options
- `mtv_help("patch planvm")` — per-VM patching flags
- `mtv_help("settings")` — settings management subcommands

Always call `mtv_help` before constructing an unfamiliar command to get the correct and current flags.

## Translating MCP Tool Calls to CLI Commands

> **Note for human users**: This section translates MCP tool calls into equivalent
> `kubectl mtv` CLI commands you can run manually in your terminal.

When showing users the equivalent CLI command, follow these rules.

### Rule 1: Base command

The `command` field maps to `kubectl mtv <command>`:

```
{command: "start plan", ...}  →  kubectl mtv start plan ...
{command: "get inventory vm", ...}  →  kubectl mtv get inventory vm ...
```

### Rule 2: Flags use `--the-flag-key` (NO positional arguments)

Every key in the `flags` object becomes a double-dash flag on the CLI:
`key: "val"` → `--key val`. `kubectl mtv` has NO positional arguments —
resource names MUST use `--name`.

```
kubectl mtv start plan --name my-migration -n ns
```

### Rule 3: Boolean flags

`true` → include the flag with no value. `false` or absent → omit it.

```
{flags: {dry-run: true}}  →  --dry-run
{flags: {all: true}}      →  --all
{flags: {vms: true}}      →  --vms
```

### Rule 4: Always append `-n <namespace>`

The MCP server injects namespace automatically, but CLI commands need it
explicitly. Always add `-n <namespace>` (or `--all-namespaces`).

### Translation examples

MCP tool call:
```
mtv_write {command: "create plan", flags: {name: "my-mig", source: "vsphere-prod", vms: "vm1,vm2"}}
```
CLI:
```
kubectl mtv create plan --name my-mig --source vsphere-prod --vms "vm1,vm2" -n <ns>
```

MCP tool call:
```
mtv_write {command: "start plan", flags: {name: "my-mig"}}
```
CLI:
```
kubectl mtv start plan --name my-mig -n <ns>
```

MCP tool call:
```
mtv_read {command: "get plan", flags: {name: "my-mig", vms: true, disk: true}}
```
CLI:
```
kubectl mtv get plan --name my-mig --vms --disk -n <ns>
```

MCP tool call:
```
mtv_read {command: "describe plan", flags: {name: "my-mig"}}
```
CLI:
```
kubectl mtv describe plan --name my-mig -n <ns>
```

MCP tool call:
```
mtv_write {command: "delete plan", flags: {name: "my-mig", clean-all: true}}
```
CLI:
```
kubectl mtv delete plan --name my-mig --clean-all -n <ns>
```

## I. Introduction and Fundamentals

| Chapter | Link | Description |
|---------|------|-------------|
| 1. Overview | [01-overview](https://yaacov.github.io/kubectl-mtv/guide/01-overview-of-kubectl-mtv) | What is kubectl-mtv, supported platforms, key features, relationship with Forklift/MTV |
| 2. Installation | [02-installation](https://yaacov.github.io/kubectl-mtv/guide/02-installation-and-prerequisites) | Krew install, binary download, build from source, global flags |
| 3. Quick Start | [03-quick-start](https://yaacov.github.io/kubectl-mtv/guide/03-quick-start-first-migration-workflow) | Full first-migration walkthrough: namespace, providers, plan, execute, monitor |
| 4. Migration Types | [04-migration-types](https://yaacov.github.io/kubectl-mtv/guide/04-migration-types-and-strategy-selection) | Cold, warm, live migration; decision framework, performance data |
| 5. Conversion Migration | [05-conversion](https://yaacov.github.io/kubectl-mtv/guide/05-conversion-migration) | External storage vendor integration, vSphere only, PVC metadata |

## II. Provider, Host, and VDDK Management

| Chapter | Link | Description |
|---------|------|-------------|
| 6. Provider Management | [06-providers](https://yaacov.github.io/kubectl-mtv/guide/06-provider-management) | Create/patch/delete providers (vSphere, oVirt, OpenStack, OpenShift), secret ownership |
| 7. Migration Hosts | [07-hosts](https://yaacov.github.io/kubectl-mtv/guide/07-migration-host-management) | ESXi host creation, IP resolution, authentication options |
| 8. VDDK Image | [08-vddk](https://yaacov.github.io/kubectl-mtv/guide/08-vddk-image-creation-and-configuration) | Build VDDK container image, `MTV_VDDK_INIT_IMAGE`, provider configuration |

## III. Inventory and Query Language

| Chapter | Link | Description |
|---------|------|-------------|
| 9. Inventory | [09-inventory](https://yaacov.github.io/kubectl-mtv/guide/09-inventory-management) | Query VMs, networks, storage, hosts; output formats; `--output planvms` export |
| 10. Query Language | [10-queries](https://yaacov.github.io/kubectl-mtv/guide/10-query-language-reference-and-advanced-filtering) | TSL WHERE, operators, functions; filter by power state, memory, concerns; sorting |

## IV. Mapping and Plan Configuration

| Chapter | Link | Description |
|---------|------|-------------|
| 11. Mapping Management | [11-mappings](https://yaacov.github.io/kubectl-mtv/guide/11-mapping-management) | Network/storage mapping creation, Multus/Pod networks, enhanced storage options |
| 12. Storage Offloading | [12-offloading](https://yaacov.github.io/kubectl-mtv/guide/12-storage-array-offloading-and-optimization) | 10x faster via IBM FlashSystem, NetApp ONTAP, Pure Storage, Dell PowerMax, HPE |
| 13. Plan Creation | [13-plans](https://yaacov.github.io/kubectl-mtv/guide/13-migration-plan-creation) | VM selection (names, file, query), inline/named/default mappings, plan flags |
| 14. PlanVMS Format | [14-planvms](https://yaacov.github.io/kubectl-mtv/guide/14-customizing-individual-vms-planvms-format) | Per-VM customization: targetName, rootDisk, instanceType, LUKS, hooks |

## V. Advanced Migration Customization

| Chapter | Link | Description |
|---------|------|-------------|
| 15. Target VM Placement | [15-placement](https://yaacov.github.io/kubectl-mtv/guide/15-target-vm-placement) | `--target-labels`, `--target-node-selector`, `--target-affinity` with KARL |
| 16. Convertor Optimization | [16-convertor](https://yaacov.github.io/kubectl-mtv/guide/16-migration-process-optimization) | Convertor pod scheduling, `--convertor-affinity`, resource sizing |
| 17. Migration Hooks | [17-hooks](https://yaacov.github.io/kubectl-mtv/guide/17-migration-hooks) | Pre/post-migration hooks, Ansible playbooks, shell scripts, `patch planvm` |
| 18. Advanced Patching | [18-patching](https://yaacov.github.io/kubectl-mtv/guide/18-advanced-plan-patching) | `patch plan` and `patch planvm` for migration type, placement, hooks |

## VI. Operations, Debugging, and AI

| Chapter | Link | Description |
|---------|------|-------------|
| 19. Plan Lifecycle | [19-lifecycle](https://yaacov.github.io/kubectl-mtv/guide/19-plan-lifecycle-execution) | Start, cutover, cancel, archive, unarchive plans |
| 20. Troubleshooting | [20-debugging](https://yaacov.github.io/kubectl-mtv/guide/20-debugging-and-troubleshooting) | Debug output, common issues, convertor pods stuck, mapping errors |
| 21. Best Practices | [21-best-practices](https://yaacov.github.io/kubectl-mtv/guide/21-best-practices-and-security) | Plan strategies, provider security, query optimization, RBAC |
| 22. MCP Server | [22-mcp](https://yaacov.github.io/kubectl-mtv/guide/22-model-context-protocol-mcp-server-integration) | AI assistant integration, stdio/HTTP modes, Claude/Cursor setup |
| 23. KubeVirt Tools | [23-kubevirt](https://yaacov.github.io/kubectl-mtv/guide/23-integration-with-kubevirt-tools) | virtctl integration for post-migration VM lifecycle |
| 24. Health Checks | [24-health](https://yaacov.github.io/kubectl-mtv/guide/24-system-health-checks) | `kubectl mtv health`, operator/controller/pod/provider/plan checks |
| 25. Settings | [25-settings](https://yaacov.github.io/kubectl-mtv/guide/25-settings-management) | `settings get/set/unset`, feature flags, performance tuning, VDDK image |

## VII. Reference and Appendices

| Chapter | Link | Description |
|---------|------|-------------|
| 26. Command Reference | [26-commands](https://yaacov.github.io/kubectl-mtv/guide/26-command-reference) | Complete command/flag reference for all kubectl-mtv commands |
| 27. TSL Reference | [27-tsl](https://yaacov.github.io/kubectl-mtv/guide/27-tsl-tree-search-language-reference) | Full TSL syntax: operators, functions, field access, SI units, quick ref card |
| 28. KARL Reference | [28-karl](https://yaacov.github.io/kubectl-mtv/guide/28-karl-kubernetes-affinity-rule-language-reference) | Full KARL syntax: rule types, topology, selectors, weight, quick ref card |

## Quick Topic Finder

Use this to match user questions to the right documentation link.

- **"How do I install kubectl-mtv?"** → [Ch 2: Installation](https://yaacov.github.io/kubectl-mtv/guide/02-installation-and-prerequisites)
- **"How do I create a provider?"** → [Ch 6: Provider Management](https://yaacov.github.io/kubectl-mtv/guide/06-provider-management)
- **"How do I list VMs / query inventory?"** → [Ch 9: Inventory](https://yaacov.github.io/kubectl-mtv/guide/09-inventory-management)
- **"How do I filter VMs with queries?"** → [Ch 10: Query Language](https://yaacov.github.io/kubectl-mtv/guide/10-query-language-reference-and-advanced-filtering) or [Ch 27: TSL Reference](https://yaacov.github.io/kubectl-mtv/guide/27-tsl-tree-search-language-reference)
- **"How do I create a migration plan?"** → [Ch 13: Plan Creation](https://yaacov.github.io/kubectl-mtv/guide/13-migration-plan-creation)
- **"What flags does create plan accept?"** → [Ch 26: Command Reference](https://yaacov.github.io/kubectl-mtv/guide/26-command-reference)
- **"How do I map networks/storage?"** → [Ch 11: Mapping Management](https://yaacov.github.io/kubectl-mtv/guide/11-mapping-management)
- **"How do I start a migration?"** → [Ch 19: Plan Lifecycle](https://yaacov.github.io/kubectl-mtv/guide/19-plan-lifecycle-execution)
- **"Cold vs warm vs live migration?"** → [Ch 4: Migration Types](https://yaacov.github.io/kubectl-mtv/guide/04-migration-types-and-strategy-selection)
- **"How do I set up VDDK?"** → [Ch 8: VDDK Image](https://yaacov.github.io/kubectl-mtv/guide/08-vddk-image-creation-and-configuration)
- **"How do I use hooks?"** → [Ch 17: Migration Hooks](https://yaacov.github.io/kubectl-mtv/guide/17-migration-hooks)
- **"How do I control VM placement / affinity?"** → [Ch 15: Target VM Placement](https://yaacov.github.io/kubectl-mtv/guide/15-target-vm-placement) or [Ch 28: KARL Reference](https://yaacov.github.io/kubectl-mtv/guide/28-karl-kubernetes-affinity-rule-language-reference)
- **"How do I patch a plan / VM?"** → [Ch 18: Advanced Patching](https://yaacov.github.io/kubectl-mtv/guide/18-advanced-plan-patching)
- **"How do I check system health?"** → [Ch 24: Health Checks](https://yaacov.github.io/kubectl-mtv/guide/24-system-health-checks)
- **"How do I configure settings?"** → [Ch 25: Settings](https://yaacov.github.io/kubectl-mtv/guide/25-settings-management)
- **"How do I customize per-VM settings?"** → [Ch 14: PlanVMS Format](https://yaacov.github.io/kubectl-mtv/guide/14-customizing-individual-vms-planvms-format)
- **"How do I optimize convertor pods?"** → [Ch 16: Convertor Optimization](https://yaacov.github.io/kubectl-mtv/guide/16-migration-process-optimization)
- **"Storage array offloading?"** → [Ch 12: Storage Offloading](https://yaacov.github.io/kubectl-mtv/guide/12-storage-array-offloading-and-optimization)
- **"Migration is failing / troubleshooting"** → [Ch 20: Troubleshooting](https://yaacov.github.io/kubectl-mtv/guide/20-debugging-and-troubleshooting)
- **"MCP server / AI integration?"** → [Ch 22: MCP Server](https://yaacov.github.io/kubectl-mtv/guide/22-model-context-protocol-mcp-server-integration)
- **"What is TSL / query syntax?"** → [Ch 27: TSL Reference](https://yaacov.github.io/kubectl-mtv/guide/27-tsl-tree-search-language-reference)
- **"What is KARL / affinity syntax?"** → [Ch 28: KARL Reference](https://yaacov.github.io/kubectl-mtv/guide/28-karl-kubernetes-affinity-rule-language-reference)
- **"Best practices / security?"** → [Ch 21: Best Practices](https://yaacov.github.io/kubectl-mtv/guide/21-best-practices-and-security)
- **"ESXi migration hosts?"** → [Ch 7: Migration Hosts](https://yaacov.github.io/kubectl-mtv/guide/07-migration-host-management)
- **"Conversion migration?"** → [Ch 5: Conversion Migration](https://yaacov.github.io/kubectl-mtv/guide/05-conversion-migration)
- **"KubeVirt / virtctl after migration?"** → [Ch 23: KubeVirt Tools](https://yaacov.github.io/kubectl-mtv/guide/23-integration-with-kubevirt-tools)
