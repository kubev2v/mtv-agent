---
name: inventory-openstack
description: OpenStack inventory field reference and TSL query examples. Use when querying OpenStack provider inventory (VMs, volumes, networks, subnets, flavors, images, projects).
---

# OpenStack Inventory Reference

Field names and query examples for OpenStack providers. Replace `<PROVIDER>` and `<NS>` with actual values.

**Key differences**: CPU/memory are determined by `flavorId` (not direct VM fields). Disk details require querying the standalone `volume` resource.

---

## VM Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | instance UUID |
| `name` | string | `"web-server-01"` |
| `status` | string | `"ACTIVE"`, `"SHUTOFF"`, `"ERROR"` |
| `tenantId` | string | project/tenant UUID |
| `hostId` | string | host hash |
| `imageId` | string | image UUID |
| `flavorId` | string | flavor UUID |
| `addresses` | object | network-keyed IP addresses |
| `attachedVolumes[*].id` | string | volume UUID |
| `fault` | object | error details (if status is ERROR) |
| `tags` | array | `["production", "web"]` |
| `securityGroups` | array | security group names |
| `concerns[*].category` | string | `"Warning"` |
| `concerns[*].label` | string | concern label |
| `concerns[*].assessment` | string | description |

---

## Volume Fields

Query with `get inventory volume --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | volume UUID |
| `name` | string | `"data-vol-01"` |
| `status` | string | `"available"`, `"in-use"`, `"error"` |
| `size` | number | `100` (GB) |
| `volumeType` | string | `"ssd"`, `"standard"` |
| `bootable` | string | `"true"`, `"false"` |
| `encrypted` | bool | `false` |
| `attachments[*]` | object | attached server details |
| `availabilityZone` | string | `"nova"` |

---

## Network Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | string | network UUID |
| `name` | string | `"internal-net"` |
| `status` | string | `"ACTIVE"` |
| `adminStateUp` | bool | `true` |
| `shared` | bool | `false` |
| `subnets` | array | subnet UUIDs |
| `tenantId` | string | project UUID |

---

## Subnet Fields

Query with `get inventory subnet --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | subnet UUID |
| `name` | string | `"internal-subnet"` |
| `networkId` | string | parent network UUID |
| `cidr` | string | `"10.0.0.0/24"` |
| `gatewayIp` | string | `"10.0.0.1"` |
| `ipVersion` | number | `4` |
| `enableDhcp` | bool | `true` |

---

## Flavor Fields

Query with `get inventory flavor --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | flavor UUID |
| `name` | string | `"m1.large"` |
| `ram` | number | `8192` (MB) |
| `vcpus` | number | `4` |
| `disk` | number | `80` (GB) |
| `swap` | number | `0` |
| `isPublic` | bool | `true` |

---

## Image Fields

Query with `get inventory image --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | image UUID |
| `name` | string | `"rhel-8.6"` |
| `status` | string | `"active"` |
| `diskFormat` | string | `"qcow2"`, `"raw"` |
| `containerFormat` | string | `"bare"` |
| `sizeBytes` | number | bytes |
| `minDiskGigabytes` | number | `10` |
| `minRamMegabytes` | number | `512` |

---

## Project Fields

Query with `get inventory project --provider <PROVIDER>`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | project UUID |
| `name` | string | `"production"` |
| `description` | string | `"Production tenant"` |
| `enabled` | bool | `true` |

---

## VM Query Examples

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where status = 'ACTIVE'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where status = 'SHUTOFF'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where flavorId = '<flavor-id>'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where len(attachedVolumes) > 1", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where name ~= 'web-.*'", "output": "markdown" } }
```

---

## Volume Query Examples

```json
mtv_read { "command": "get inventory volume", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where bootable = 'true'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory volume", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where status = 'available' and size > 100", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory volume", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where volumeType = 'ssd'", "output": "markdown" } }
```

---

## Infrastructure Query Examples

```json
mtv_read { "command": "get inventory flavor", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where vcpus >= 4 and ram >= 8192", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory network", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where shared = true", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory subnet", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where ipVersion = 4", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory image", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where status = 'active' and diskFormat = 'qcow2'", "output": "markdown" } }
```
