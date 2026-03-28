---
name: inventory-openshift
description: OpenShift (target) inventory field reference and TSL query examples. Use when querying OpenShift/KubeVirt target provider inventory (VMs, NADs, StorageClasses, namespaces, PVCs, DataVolumes).
---

# OpenShift Inventory Reference

Field names and query examples for OpenShift target providers. The OpenShift provider is typically named `"host"` in MTV.

Replace `<NS>` with the MTV operator namespace (where providers are defined).

---

## VM Fields

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `"fedora-vm"` |
| `id` | string | `"04a6e0e3-..."` |
| `namespace` | string | `"mtv-test"` |

---

## Network (NAD) Fields

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `"default"` |
| `id` | string | `"b4f1689d-..."` |
| `namespace` | string | `"openshift-ovn-kubernetes"` |

---

## Storage (StorageClass) Fields

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `"ocs-storagecluster-ceph-rbd"` |
| `id` | string | `"a8b1ef0c-..."` |
| `object.provisioner` | string | `"openshift-storage.rbd.csi.ceph.com"` |
| `object.reclaimPolicy` | string | `"Delete"` |
| `object.volumeBindingMode` | string | `"Immediate"`, `"WaitForFirstConsumer"` |
| `object.allowVolumeExpansion` | bool | `true` |

---

## Namespace Fields

Query with `get inventory namespace --provider host`.

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `"mtv-test"` |
| `id` | string | namespace UID |

---

## PVC Fields

Query with `get inventory pvc --provider host`.

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `"data-pvc"` |
| `id` | string | PVC UID |
| `namespace` | string | `"mtv-test"` |

---

## DataVolume Fields

Query with `get inventory data-volume --provider host`.

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `"rhel8-dv"` |
| `id` | string | DataVolume UID |
| `namespace` | string | `"mtv-test"` |

---

## Target Storage Query Examples

```json
mtv_read { "command": "get inventory storage", "flags": { "provider": "host", "namespace": "<NS>", "query": "where name ~= '.*ceph.*'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory storage", "flags": { "provider": "host", "namespace": "<NS>", "query": "where object.volumeBindingMode = 'WaitForFirstConsumer'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory storage", "flags": { "provider": "host", "namespace": "<NS>", "query": "where object.allowVolumeExpansion = true", "output": "markdown" } }
```

---

## Target Network Query Examples

```json
mtv_read { "command": "get inventory network", "flags": { "provider": "host", "namespace": "<NS>", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory network", "flags": { "provider": "host", "namespace": "<NS>", "query": "where namespace = 'default'", "output": "markdown" } }
```

---

## Other Target Queries

```json
mtv_read { "command": "get inventory namespace", "flags": { "provider": "host", "namespace": "<NS>", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "host", "namespace": "<NS>", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory pvc", "flags": { "provider": "host", "namespace": "<NS>", "query": "where namespace = 'mtv-test'", "output": "markdown" } }
```
