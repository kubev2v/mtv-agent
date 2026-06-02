---
name: inventory-hyperv
description: Hyper-V inventory field reference and TSL query examples. Use when querying Hyper-V provider inventory (VMs, disks, networks, storage).
---

# Hyper-V Inventory Reference

Field names and query examples for Hyper-V providers. Replace `<PROVIDER>` and `<NS>` with actual values.

---

## VM Fields

### Identity and State

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | `"win-server-01"` |
| `variant` | string | `"hyperv"` |
| `path` | string | resource path |
| `uuid` | string | VM UUID |
| `powerState` | string | `"Running"`, `"Off"`, `"Paused"` |

### Compute

| Field | Type | Example |
|-------|------|---------|
| `cpuCount` | number | `4` |
| `memoryMB` | number | `8192` |

### Guest and Firmware

| Field | Type | Example |
|-------|------|---------|
| `guestOS` | string | `"Windows Server 2022"` |
| `firmware` | string | `"efi"`, `"bios"` |
| `secureBoot` | bool | `true` |
| `tpmEnabled` | bool | `true` |

### Checkpoint

| Field | Type | Example |
|-------|------|---------|
| `hasCheckpoint` | bool | `false` |

### Disks (`disks[*]`)

| Field | Type | Example |
|-------|------|---------|
| `disks[*].id` | string | disk ID |
| `disks[*].windowsPath` | string | `"C:\\VMs\\disk.vhdx"` |
| `disks[*].smbPath` | string | SMB share path |
| `disks[*].capacity` | number | bytes |
| `disks[*].format` | string | `"vhdx"`, `"vhd"` |
| `disks[*].rctEnabled` | bool | `true` |

### NICs (`nics[*]`)

| Field | Type | Example |
|-------|------|---------|
| `nics[*].name` | string | `"Network Adapter"` |
| `nics[*].mac` | string | `"00:15:5D:01:02:03"` |
| `nics[*].deviceIndex` | number | `0` |
| `nics[*].networkUUID` | string | virtual switch UUID |
| `nics[*].networkName` | string | `"Default Switch"` |

### Guest Networks (`guestNetworks[*]`)

| Field | Type | Example |
|-------|------|---------|
| `guestNetworks[*].mac` | string | MAC address |
| `guestNetworks[*].ip` | string | `"10.0.0.5"` |
| `guestNetworks[*].deviceIndex` | number | `0` |
| `guestNetworks[*].origin` | string | origin |
| `guestNetworks[*].prefix` | number | CIDR prefix |
| `guestNetworks[*].dns` | string | DNS server |
| `guestNetworks[*].gateway` | string | gateway IP |

### Concerns

| Field | Type | Example |
|-------|------|---------|
| `concerns[*].category` | string | `"Warning"` |
| `concerns[*].label` | string | concern label |
| `concerns[*].message` | string | description |

---

## Disk Fields (standalone resource)

Query with `get inventory disk --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | disk ID |
| `name` | string | disk name |
| `windowsPath` | string | `"C:\\VMs\\disk.vhdx"` |
| `smbPath` | string | SMB share path |
| `capacity` | number | bytes |
| `format` | string | `"vhdx"`, `"vhd"` |
| `rctEnabled` | bool | `true` |
| `datastore` | string | storage reference |

---

## Network Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | network ID |
| `name` | string | `"Default Switch"` |
| `uuid` | string | virtual switch UUID |
| `switchName` | string | switch name |
| `switchType` | string | `"Internal"`, `"External"`, `"Private"` |
| `description` | string | switch description |

---

## Storage Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | storage ID |
| `name` | string | `"C:\\VMs"` |
| `type` | string | storage type |
| `path` | string | file system path |
| `capacity` | number | bytes |
| `free` | number | bytes |

---

## VM Query Examples

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where powerState = 'Running'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where memoryMB > 4096", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where hasCheckpoint = true", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where any(disks[*].format = 'vhdx')", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where secureBoot = true and tpmEnabled = true", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where name ~= 'win-.*'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where cpuCount >= 4 order by memoryMB desc limit 10", "output": "markdown" } }
```

---

## Disk Query Examples

```json
mtv_read { "command": "get inventory disk", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where format = 'vhdx'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory disk", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where rctEnabled = true", "output": "markdown" } }
```

---

## Network Query Examples

```json
mtv_read { "command": "get inventory network", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where switchType = 'External'", "output": "markdown" } }
```
