---
name: observe-metrics
description: Observe cluster metrics via Prometheus/Thanos. Use when the user wants to check cluster metrics, monitor network traffic, storage I/O, pod resource usage, VM migration throughput, or discover available Prometheus metrics. Covers metric discovery, storage (Ceph/ODF), network traffic by namespace/pod, pod statistics, and Forklift/MTV migration monitoring.
---

# Observe Cluster Metrics

Use the **kubectl-metrics** MCP server tools to query Prometheus/Thanos.

| Tool | Server | Purpose |
|------|--------|---------|
| `metrics_read` | user-kubectl-metrics | Execute queries, run presets, discover metrics |
| `metrics_help` | user-kubectl-metrics | Get flag details, list presets, PromQL reference |

For detailed per-domain queries, labels, and metrics tables see the `observe-metrics-reference` skill.

## Self-Learning Rule

Before using an unfamiliar subcommand, call `metrics_help` first:

```json
metrics_help { "command": "<subcommand>" }
```

Omit `command` to get an overview of all subcommands and available presets.

## Output Format Rule

All query commands accept an `output` flag:

| Format | Use when |
|--------|----------|
| `markdown` | Default. Best for presenting results to the user. |
| `table` | Compact tabular display. |
| `json` | You need to parse or process results programmatically. |
| `raw` | You need the full Prometheus API response as-is. |

**Always use `output: "markdown"` (or omit for default) when presenting to the user.**
Use `output: "json"` only when you need to extract specific fields for further processing.

## Post-Query Filtering with `selector`

The `selector` flag filters results **after** the query runs, using label matching:

```json
metrics_read { "command": "query", "flags": { "query": "up", "selector": "namespace=prod,job=~prom.*", "output": "markdown" } }
```

Supported operators: `=` (equal), `!=` (not equal), `=~` (regex match), `!~` (negative regex).

## Pivot Tables for Range Queries

Range queries use a **pivot table** by default (one column per label combination).
Set `no_pivot: true` to get the traditional row-per-sample format:

```json
metrics_read { "command": "query_range", "flags": { "query": "up", "start": "-1h", "no_pivot": true, "output": "markdown" } }
```

---

## Discover Available Metrics

### List all metric names

```json
metrics_read { "command": "discover", "flags": { "output": "markdown" } }
```

### Search metrics by keyword

```json
metrics_read { "command": "discover", "flags": { "keyword": "network", "output": "markdown" } }
```

### Group metrics by prefix (overview)

```json
metrics_read { "command": "discover", "flags": { "keyword": "ceph", "group_by_prefix": true, "output": "markdown" } }
```

### List labels for a specific metric

```json
metrics_read { "command": "labels", "flags": { "metric": "container_network_receive_bytes_total", "output": "markdown" } }
```

---

## How to Query

### Instant query (point-in-time)

```json
metrics_read { "command": "query", "flags": { "query": "YOUR_PROMQL_HERE", "output": "markdown" } }
```

### Range query (last 1 hour, default steps)

```json
metrics_read { "command": "query_range", "flags": { "query": "YOUR_PROMQL_HERE", "start": "-1h", "output": "markdown" } }
```

### Range query with custom window

```json
metrics_read {
  "command": "query_range",
  "flags": {
    "query": "YOUR_PROMQL_HERE",
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-01T06:00:00Z",
    "step": "300s",
    "output": "markdown"
  }
}
```

### With explicit output format

```json
metrics_read { "command": "query", "flags": { "query": "up", "output": "json" } }
```

---

## Pre-configured Queries (Presets)

Use `metrics_help` with no command to list all available presets:

```json
metrics_help {}
```

Run a preset by name:

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_migration_status", "output": "markdown" } }
```

Many presets accept a `namespace` filter:

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_migration_pod_rx", "namespace": "openshift-mtv", "output": "markdown" } }
```

Filter preset results with `selector`:

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_migration_pod_rx", "selector": "pod=~virt-v2v.*", "output": "markdown" } }
```

Promote an instant preset to a range query by passing `start`:

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_migration_status", "start": "-2h", "step": "30s", "output": "markdown" } }
```

### Available presets

| Preset | Type | Description |
|--------|------|-------------|
| `mtv_migration_status` | instant | Migration counts by status |
| `mtv_plan_status` | instant | Plan-level status counts |
| `mtv_data_transferred` | instant | Total bytes migrated per plan |
| `mtv_net_throughput` | instant | Migration network throughput |
| `mtv_storage_throughput` | instant | Migration storage throughput |
| `mtv_migration_duration` | instant | Migration duration per plan (seconds) |
| `mtv_migration_pod_rx` | instant | Migration pod receive rate (bytes/sec, top 20) |
| `mtv_migration_pod_tx` | instant | Migration pod transmit rate (bytes/sec, top 20) |
| `mtv_forklift_traffic` | instant | Forklift operator pod network traffic |
| `mtv_namespace_network_rx` | instant | Top 10 namespaces by network receive rate |
| `mtv_namespace_network_tx` | instant | Top 10 namespaces by network transmit rate |
| `mtv_network_errors` | instant | Network errors + drops by namespace (top 10) |
| `mtv_vmi_migrations_pending` | instant | KubeVirt VMI migrations in pending phase |
| `mtv_vmi_migrations_running` | instant | KubeVirt VMI migrations in running phase |
| `mtv_net_throughput_over_time` | range | Migration network throughput trend |
| `mtv_storage_throughput_over_time` | range | Migration storage throughput trend |
| `mtv_data_transferred_over_time` | range | Data transfer progress over time |
| `mtv_migration_status_over_time` | range | Migration status counts over time |
| `mtv_migration_pod_rx_over_time` | range | Migration pod receive rate trend (top 20) |
| `mtv_namespace_network_rx_over_time` | range | Top 10 namespaces by RX rate trend |

---

## PromQL Quick Reference

Use this reference to compose custom queries with `metrics_read`.

### Selecting metrics

```
metric_name                          # all time series for this metric
metric_name{label="value"}           # filter by exact label match
metric_name{label=~"pattern.*"}      # filter by regex match
metric_name{label!="value"}          # exclude a label value
metric_name{l1="a", l2="b"}         # combine multiple filters
```

### Rate and increase (for counters)

Counters only go up. Use `rate` or `increase` to get meaningful values:

```
rate(metric[5m])                     # per-second rate over 5 minutes
increase(metric[1h])                 # total increase over 1 hour
```

### Aggregation

```
sum(metric)                          # total across all series
sum by (label)(metric)               # total grouped by label
avg by (label)(metric)               # average grouped by label
count by (label)(metric)             # count of series grouped by label
min by (label)(metric)               # minimum grouped by label
max by (label)(metric)               # maximum grouped by label
```

### Sorting and limiting

```
topk(10, metric)                     # top 10 series by value
bottomk(5, metric)                   # bottom 5 series by value
sort_desc(metric)                    # sort descending
```

### Arithmetic

```
metric_a / metric_b                  # ratio of two metrics
metric * 100                         # scale a metric
1 - (available / total)              # compute used percentage
```

### Combining techniques

```json
metrics_read {
  "command": "query",
  "flags": { "query": "topk(10, sort_desc(sum by (namespace)(rate(container_network_receive_bytes_total[5m]))))", "output": "markdown" }
}
```

```json
metrics_read {
  "command": "query",
  "flags": { "query": "rate(ceph_osd_op_latency_sum[5m]) / rate(ceph_osd_op_latency_count[5m])", "output": "markdown" }
}
```

```json
metrics_read {
  "command": "query",
  "flags": { "query": "100 - avg by (instance)(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100", "output": "markdown" }
}
```
