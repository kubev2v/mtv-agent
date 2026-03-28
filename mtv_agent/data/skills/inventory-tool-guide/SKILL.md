---
name: inventory-tool-guide
description: Guide for querying MTV provider inventory with TSL. Covers available resources per provider, output formats, TSL syntax, common pitfalls, and using inventory for network/storage mapping. Use when querying provider inventory.
---

# Inventory Tool Guide

Use `mtv_read` with `get inventory RESOURCE` to query provider inventory. Use `mtv_help` for unfamiliar commands.

For field references and ready-to-use queries, load the appropriate per-provider skill:
`inventory-vsphere`, `inventory-ovirt`, `inventory-openstack`, `inventory-ec2`, `inventory-ova`, `inventory-hyperv`, `inventory-openshift`.

---

## Common Pitfalls

1. **`flags` must be a JSON object** — never pass it as a string.
   - Correct: `"flags": {"namespace": "mtv", "output": "markdown"}`
   - Wrong: `"flags": "{namespace: mtv, output: markdown}"`
2. **Only use documented parameters** — never invent flags like `fields`. Run `mtv_help("get inventory vm")` to see valid flags.
3. **Discovering fields** — use `"output": "json"` with `"query": "limit 1"` to inspect one object and see all available field names.
4. **oVirt disk types live on a standalone resource** — query `get inventory disk`, not the VM's `diskAttachments`, to find `storageType = 'lun'`.
5. **EC2 and OVA use PascalCase field names** — unlike vSphere/oVirt/OpenStack which use camelCase.

---

## Provider Field Differences

| Concept     | vSphere        | oVirt                             | OpenStack              | EC2                    | OVA                  | HyperV               | OpenShift           |
| ----------- | -------------- | --------------------------------- | ---------------------- | ---------------------- | -------------------- | -------------------- | ------------------- |
| Power       | `powerState`   | `status`                          | `status`               | `State.Name`           | N/A                  | `powerState`         | N/A (k8s)           |
| Memory      | `memoryMB`     | `memory` (bytes!)                 | via `flavorId`         | via `InstanceType`     | `memoryMB`           | `memoryMB`           | N/A (k8s)           |
| CPU         | `cpuCount`     | `cpuSockets * cpuCores`           | via `flavorId`         | via `InstanceType`     | `cpuCount`           | `cpuCount`           | N/A (k8s)           |
| Disks on VM | `disks[*]`     | `diskAttachments[*]`              | `attachedVolumes[*]`   | `BlockDeviceMappings`  | `disks[*]`           | `disks[*]`           | N/A                 |
| Standalone  | N/A            | `get inventory disk`              | `get inventory volume` | `get inventory volume` | `get inventory disk` | `get inventory disk` | `get inventory pvc` |
| LUN/RDM     | `disks[*].rdm` | `disk.storageType` + `lunStorage` | N/A                    | N/A                    | N/A                  | N/A                  | N/A                 |
| Field case  | camelCase      | camelCase                         | camelCase              | PascalCase (AWS)       | PascalCase (OVF)     | camelCase            | k8s objects         |

---

## Resource Availability Matrix

| Resource     | vSphere       | oVirt             | OpenStack      | EC2           | OVA | HyperV | OpenShift        |
| ------------ | ------------- | ----------------- | -------------- | ------------- | --- | ------ | ---------------- |
| vm           | Y             | Y                 | Y              | Y (instance)  | Y   | Y      | Y                |
| network      | Y             | Y                 | Y              | Y (subnet)    | Y   | Y      | Y (NAD)          |
| storage      | Y (datastore) | Y (storageDomain) | Y (volumeType) | Y (EBS types) | Y   | Y      | Y (storageClass) |
| disk         | --            | Y                 | --             | --            | Y   | Y      | --               |
| volume       | --            | --                | Y              | Y             | --  | --     | --               |
| host         | Y             | Y                 | --             | --            | --  | --     | --               |
| cluster      | Y             | Y                 | --             | --            | --  | --     | --               |
| datacenter   | Y             | Y                 | --             | --            | --  | --     | --               |
| folder       | Y             | --                | --             | --            | --  | --     | --               |
| disk-profile | --            | Y                 | --             | --            | --  | --     | --               |
| nic-profile  | --            | Y                 | --             | --            | --  | --     | --               |
| flavor       | --            | --                | Y              | --            | --  | --     | --               |
| image        | --            | --                | Y              | --            | --  | --     | --               |
| project      | --            | --                | Y              | --            | --  | --     | --               |
| subnet       | --            | --                | Y              | --            | --  | --     | --               |
| namespace    | --            | --                | --             | --            | --  | --     | Y                |
| pvc          | --            | --                | --             | --            | --  | --     | Y                |
| data-volume  | --            | --                | --             | --            | --  | --     | Y                |

---

## Output Formats

| Format | Use when |
|--------|----------|
| `markdown` | Presenting results to the user (default). |
| `json` | Parsing results or discovering fields. |
| `table` | Compact display. |
| `yaml` | Structured output. |
| `planvms` | Export for `create plan --vms @file`. |

---

## TSL Query Syntax

Structure: `[SELECT fields] WHERE condition [ORDER BY field [ASC|DESC]] [LIMIT n]`

### Operators

- **Comparison**: `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`
- **String**: `like` (% wildcard), `ilike` (case-insensitive), `~=` (regex), `~!` (regex not)
- **Logical**: `and`, `or`, `not`
- **Set**: `in [...]`, `not in [...]`, `between X and Y`
- **Null**: `is null`, `is not null`

### Array Functions

- `len(field)` -- array length: `where len(disks) > 1`
- `any(field[*].sub = 'val')` -- any element matches: `where any(concerns[*].category = 'Critical')`
- `all(field[*].sub >= N)` -- all elements match
- `sum(field[*].sub)` -- sum of values: `where sum(disks[*].capacity) > 100Gi`

### Array Access

- `field[0]` -- index access
- `field[*].sub` -- wildcard across elements
- `field.sub` -- implicit traversal (same as `field[*].sub`)

### SI Units

`Ki` (1024), `Mi` (1024^2), `Gi` (1024^3), `Ti` (1024^4)

---

## Using Inventory for Mapping

### Network mapping

1. List source networks: `get inventory network` with source provider
2. List target NADs: `get inventory network` with `provider: "host"`
3. Match by name, use in `create mapping network`

```json
mtv_read { "command": "get inventory network", "flags": { "provider": "<SOURCE>", "namespace": "<NS>", "output": "json" } }
```

### Storage mapping

1. List source datastores: `get inventory datastore` with source provider
2. List target StorageClasses: `get inventory storage` with `provider: "host"`
3. Match by name, use in `create mapping storage`

```json
mtv_read { "command": "get inventory datastore", "flags": { "provider": "<SOURCE>", "namespace": "<NS>", "output": "json" } }
```
