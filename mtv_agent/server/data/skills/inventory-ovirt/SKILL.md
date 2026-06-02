---
name: inventory-ovirt
description: oVirt (RHV) inventory field reference and TSL query examples. Use when querying oVirt/RHV provider inventory (VMs, disks, networks, storage domains, hosts, clusters).
---

# oVirt Inventory Reference

Field names and query examples for oVirt (RHV) providers. Replace `<PROVIDER>` and `<NS>` with actual values.

**Key differences from vSphere**: power state is `status` (not `powerState`), memory is in bytes (not MB), disk details require querying the standalone `disk` resource.

---

## VM Fields

### Identity and State

| Field | Type | Example |
|-------|------|---------|
| `id` | string | `"abc123-..."` |
| `name` | string | `"rhel8-prod"` |
| `description` | string | `"Production RHEL 8 VM"` |
| `path` | string | `"/ovirt/vms/rhel8-prod"` |
| `status` | string | `"up"`, `"down"`, `"unknown"` |
| `cluster` | string | cluster ID |
| `host` | string | host ID |

### Compute

| Field | Type | Example |
|-------|------|---------|
| `cpuSockets` | number | `2` |
| `cpuCores` | number | `4` |
| `cpuThreads` | number | `1` |
| `cpuShares` | number | `1024` |
| `cpuAffinity` | array | `[]` |
| `cpuPinningPolicy` | string | `"none"`, `"manual"`, `"resize_and_pin"`, `"dedicated"` |

### Memory

| Field | Type | Example |
|-------|------|---------|
| `memory` | number | `4294967296` (bytes — 4 GiB) |
| `balloonedMemory` | bool | `true` |

### Guest and BIOS

| Field | Type | Example |
|-------|------|---------|
| `guestName` | string | `"Red Hat Enterprise Linux 8"` |
| `guest.distribution` | string | `"Red Hat Enterprise Linux"` |
| `guest.fullVersion` | string | `"8.6"` |
| `osType` | string | `"rhel_8x64"` |
| `bios` | string | `"q35_ovmf"`, `"q35_sea_bios"`, `"i440fx_sea_bios"` |
| `display` | string | `"vnc"`, `"spice"` |

### Storage and HA

| Field | Type | Example |
|-------|------|---------|
| `hasIllegalImages` | bool | `false` |
| `leaseStorageDomain` | string | `""` |
| `haEnabled` | bool | `true` |
| `usbEnabled` | bool | `false` |
| `bootMenuEnabled` | bool | `false` |
| `ioThreads` | number | `0` |
| `stateless` | bool | `false` |
| `placementPolicyAffinity` | string | `"migratable"` |

### DiskAttachments (`diskAttachments[*]`)

| Field | Type | Example |
|-------|------|---------|
| `diskAttachments[*].id` | string | attachment ID |
| `diskAttachments[*].disk` | string | disk ID (use to query standalone `disk` resource) |
| `diskAttachments[*].interface` | string | `"virtio"`, `"virtio_scsi"`, `"sata"` |
| `diskAttachments[*].bootable` | bool | `true` |
| `diskAttachments[*].scsiReservation` | bool | `false` |

### NICs (`nics[*]`)

| Field | Type | Example |
|-------|------|---------|
| `nics[*].id` | string | NIC ID |
| `nics[*].name` | string | `"nic1"` |
| `nics[*].interface` | string | `"virtio"` |
| `nics[*].plugged` | bool | `true` |
| `nics[*].ipAddress[*].address` | string | `"10.0.0.5"` |
| `nics[*].ipAddress[*].version` | string | `"v4"` |
| `nics[*].profile` | string | profile ID |
| `nics[*].mac` | string | `"00:1a:4a:16:01:56"` |

### Snapshots and Concerns

| Field | Type | Example |
|-------|------|---------|
| `snapshots[*].id` | string | snapshot ID |
| `snapshots[*].description` | string | `"before upgrade"` |
| `snapshots[*].type` | string | `"regular"`, `"active"` |
| `snapshots[*].persistMemory` | bool | `false` |
| `concerns[*].id` | string | `"ovirt.ha.disabled"` |
| `concerns[*].label` | string | `"HA not enabled"` |
| `concerns[*].category` | string | `"Warning"` |
| `concerns[*].assessment` | string | description text |

### Host Devices

| Field | Type | Example |
|-------|------|---------|
| `hostDevices[*].capability` | string | `"pci"` |
| `hostDevices[*].product` | string | device name |
| `hostDevices[*].vendor` | string | vendor name |

---

## Disk Fields (standalone resource)

Query with `get inventory disk --provider <PROVIDER>`. This is the **only** way to get `storageType` and LUN details.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | disk ID |
| `name` | string | `"rhel8-os-disk"` |
| `description` | string | `"OS disk"` |
| `shared` | bool | `false` |
| `storageDomain` | string | storage domain ID |
| `profile` | string | disk profile ID |
| `provisionedSize` | number | bytes |
| `actualSize` | number | bytes |
| `storageType` | string | `"image"`, `"lun"`, `"cinder"` |
| `status` | string | `"ok"`, `"locked"` |
| `lunStorage.logicalUnit[*].lunId` | string | LUN ID |
| `lunStorage.logicalUnit[*].address` | string | iSCSI target address |
| `lunStorage.logicalUnit[*].port` | number | iSCSI port |
| `lunStorage.logicalUnit[*].target` | string | iSCSI target IQN |
| `lunStorage.logicalUnit[*].size` | number | bytes |

---

## Network Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | network ID |
| `name` | string | `"ovirtmgmt"` |
| `dataCenter` | string | datacenter ID |
| `vlan` | string | VLAN ID |
| `usages` | array | `["vm", "management"]` |
| `nicProfiles` | array | associated NIC profile IDs |

---

## StorageDomain Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | domain ID |
| `name` | string | `"nfs-data"` |
| `dataCenter` | string | datacenter ID |
| `type` | string | `"data"`, `"iso"`, `"export"` |
| `capacity` | number | bytes |
| `free` | number | bytes |
| `storage.type` | string | `"nfs"`, `"iscsi"`, `"fcp"` |

---

## Host Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | host ID |
| `name` | string | `"rhv-host-01"` |
| `cluster` | string | cluster ID |
| `status` | string | `"up"`, `"maintenance"` |
| `productName` | string | `"RHEL"` |
| `productVersion` | string | `"4.4"` |
| `inMaintenance` | bool | `false` |
| `cpuSockets` | number | `2` |
| `cpuCores` | number | `16` |

---

## Cluster Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | cluster ID |
| `name` | string | `"Default"` |
| `dataCenter` | string | datacenter ID |
| `haReservation` | bool | `false` |
| `ksmEnabled` | bool | `true` |
| `biosType` | string | `"q35_ovmf"` |
| `cpu.architecture` | string | `"x86_64"` |
| `cpu.type` | string | `"Intel Cascadelake Server"` |
| `version.major` | number | `4` |
| `version.minor` | number | `7` |

---

## DiskProfile Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | profile ID |
| `name` | string | `"default-profile"` |
| `storageDomain` | string | storage domain ID |
| `qos` | string | QoS ID |

---

## NICProfile Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | profile ID |
| `name` | string | `"ovirtmgmt-profile"` |
| `network` | string | network ID |
| `networkFilter` | string | filter ID |
| `portMirroring` | bool | `false` |
| `qos` | string | QoS ID |
| `passThrough` | bool | `false` |

---

## VM Query Examples

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where status = 'up' and memory > 4Gi", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where len(diskAttachments) > 1", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where any(diskAttachments[*].interface = 'virtio_scsi')", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where guest.distribution ~= 'Red Hat.*'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where haEnabled = true", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where bios = 'q35_ovmf'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where status = 'up' order by memory desc limit 10", "output": "markdown" } }
```

---

## Disk Query Examples

To find LUN-type disks, query the standalone `disk` resource — **not** the VM's `diskAttachments`:

```json
mtv_read { "command": "get inventory disk", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where storageType = 'lun'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory disk", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where shared = true", "output": "markdown" } }
```

**Cross-referencing pattern**: Query VMs for diskAttachment IDs, then query the `disk` resource by ID to get `storageType` details.
