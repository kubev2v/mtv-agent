---
name: inventory-ova
description: OVA inventory field reference and TSL query examples. Use when querying OVA provider inventory (VMs, disks, networks, storage).
---

# OVA Inventory Reference

Field names and query examples for OVA providers. Replace `<PROVIDER>` and `<NS>` with actual values.

**Key differences**: OVA nested model types use **PascalCase** field names (untagged Go struct fields from OVF parsing), unlike vSphere/oVirt which use camelCase.

---

## VM Fields

### Identity

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | `"exported-vm"` |
| `variant` | string | `"ova"` |
| `path` | string | resource path |
| `ovfPath` | string | path to OVF file |
| `exportSource` | string | export origin |
| `uuid` | string | VM UUID |

### Compute

| Field | Type | Example |
|-------|------|---------|
| `cpuCount` | number | `4` |
| `coresPerSocket` | number | `2` |
| `memoryMB` | number | `8192` |
| `memoryUnits` | string | `"MB"` |
| `cpuUnits` | string | `"cores"` |

### Guest and Firmware

| Field | Type | Example |
|-------|------|---------|
| `osType` | string | `"rhel_8x64"` |
| `firmware` | string | `"efi"`, `"bios"` |
| `secureBoot` | bool | `false` |

### Features

| Field | Type | Example |
|-------|------|---------|
| `cpuHotAddEnabled` | bool | `false` |
| `cpuHotRemoveEnabled` | bool | `false` |
| `memoryHotAddEnabled` | bool | `false` |
| `faultToleranceEnabled` | bool | `false` |
| `changeTrackingEnabled` | bool | `false` |
| `balloonedMemory` | number | `0` |
| `storageUsed` | number | bytes |

### Disks (`disks[*]`)

OVA disk fields use PascalCase:

| Field | Type | Example |
|-------|------|---------|
| `disks[*].ID` | string | disk ID |
| `disks[*].Name` | string | `"disk-0"` |
| `disks[*].FilePath` | string | `"disk1.vmdk"` |
| `disks[*].Capacity` | number | bytes |
| `disks[*].CapacityAllocationUnits` | string | `"byte * 2^30"` |
| `disks[*].DiskId` | string | OVF disk reference |
| `disks[*].FileRef` | string | OVF file reference |
| `disks[*].Format` | string | `"http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized"` |
| `disks[*].PopulatedSize` | number | bytes |

### NICs (`nics[*]`)

| Field | Type | Example |
|-------|------|---------|
| `nics[*].Name` | string | `"ethernet0"` |
| `nics[*].MAC` | string | `"00:50:56:be:aa:bb"` |
| `nics[*].Network` | string | network name |
| `nics[*].Config[*].Key` | string | config key |
| `nics[*].Config[*].Value` | string | config value |

### Networks (`networks[*]`)

| Field | Type | Example |
|-------|------|---------|
| `networks[*].ID` | string | network ID |
| `networks[*].Name` | string | `"VM Network"` |
| `networks[*].Description` | string | network description |

### Devices and Concerns

| Field | Type | Example |
|-------|------|---------|
| `devices[*].Kind` | string | device type |
| `concerns[*].id` | string | concern ID |
| `concerns[*].label` | string | concern label |
| `concerns[*].category` | string | `"Warning"` |
| `concerns[*].assessment` | string | description |

---

## Disk Fields (standalone resource)

Query with `get inventory disk --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | disk name |
| `variant` | string | `"ova"` |
| `path` | string | resource path |
| `FilePath` | string | `"disk1.vmdk"` |
| `Capacity` | number | bytes |
| `CapacityAllocationUnits` | string | `"byte * 2^30"` |
| `DiskId` | string | OVF disk reference |
| `FileRef` | string | OVF file reference |
| `Format` | string | VMDK format URI |
| `PopulatedSize` | number | bytes |

---

## Network Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | `"VM Network"` |
| `variant` | string | `"ova"` |
| `Description` | string | network description |

---

## Storage Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | storage name |
| `variant` | string | `"ova"` |

---

## VM Query Examples

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where cpuCount >= 4", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where memoryMB > 8192", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where firmware = 'efi'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where name ~= 'prod-.*'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where len(disks) > 1", "output": "markdown" } }
```
