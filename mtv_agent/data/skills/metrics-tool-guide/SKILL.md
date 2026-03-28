---
name: metrics-tool-guide
description: "Guide for using the Prometheus/Thanos metrics tools: output rules, query syntax, filtering, discovery, and PromQL reference. Use when the user wants to check cluster metrics and you need to know how to call metrics_read and metrics_help."
---

# Metrics Tool Guide

Use the **kubectl-metrics** MCP server tools to query Prometheus/Thanos.

| Tool | Server | Purpose |
|------|--------|---------|
| `metrics_read` | user-kubectl-metrics | Execute queries, run presets, discover metrics |
| `metrics_help` | user-kubectl-metrics | Get flag details, list presets, PromQL reference |

For ready-to-use queries, preset catalog, and metric name/label references see the `metrics-query-cookbook` skill.

## Presentation Rules

### Name every metric

When presenting query results, always tell the user what metric was queried and what it measures. For example say "**Ceph cluster health** (`ceph_health_status`): 0 = OK" rather than dumping a raw table without context.

### Batch related queries

When multiple related metrics are needed (e.g. RX + TX, CPU + memory), use the multi-query feature of `query_range` instead of making separate calls:

```json
metrics_read {
  "command": "query_range",
  "flags": {
    "query": [
      "sum by (namespace)(rate(container_network_receive_bytes_total[5m]))",
      "sum by (namespace)(rate(container_network_transmit_bytes_total[5m]))"
    ],
    "name": ["rx_bytes_per_sec", "tx_bytes_per_sec"],
    "start": "-1h",
    "output": "markdown"
  }
}
```

Each query's results are labeled with the corresponding `name`. If `name` is omitted, auto-generated labels (q1, q2, ...) are used.

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

**Always use `output: "markdown"` when presenting results to the user.**
Use `output: "json"` only when you need to extract specific fields for further processing.

## Migration Pod Discovery

Before querying network metrics for migration pods, **discover the actual pod names first**. Migration pods are named `{plan-name}-{vm-id}-{random}` (e.g. `test-vmware-metrics-vm-43-tws62`), not `virt-v2v-*` or `populator-*`.

1. List VMware/general migration pods (carry a `plan` label):

```json
debug_read { "command": "list", "flags": { "resource": "pods", "namespace": "<NAMESPACE>", "selector": "plan", "output": "markdown" } }
```

2. List oVirt/OpenStack populator pods (named `populate-{uuid}-...`):

```json
debug_read { "command": "list", "flags": { "resource": "pods", "namespace": "<NAMESPACE>", "query": "where name ~= '^populate-'", "output": "markdown" } }
```

3. Use the discovered pod names in PromQL queries (replace `POD1|POD2` with the actual names from steps 1-2):

```json
metrics_read { "command": "query", "flags": { "query": "sum by (pod)(rate(container_network_receive_bytes_total{namespace=\"<NAMESPACE>\",pod=~\"POD1|POD2\"}[5m]))", "output": "markdown" } }
```

## Short-Lived Pod Network Metrics

Container-level network metrics (`container_network_*`) require cadvisor to establish network namespace tracking, which takes 1-2 collection cycles (~10-20s). Pods that run under ~60 seconds (e.g. oVirt/OpenStack populator pods) may complete before tracking starts. CPU and memory metrics are unaffected because they are read from persistent cgroup files.

When container-level network metrics are missing for a short-lived pod, use these alternatives (ordered by signal quality):

**1. Node-level network metrics** (best for measuring transfer throughput):

Determine which node ran the pod, then query the node's aggregated RX and TX rates during the migration window:

```json
metrics_read {
  "command": "query_range",
  "flags": {
    "query": [
      "instance:node_network_receive_bytes_excluding_lo:rate1m{instance=~\"NODE_NAME.*\"}",
      "instance:node_network_transmit_bytes_excluding_lo:rate1m{instance=~\"NODE_NAME.*\"}"
    ],
    "name": ["node_rx", "node_tx"],
    "start": "<MIGRATION_START>",
    "end": "<MIGRATION_END>",
    "step": "30s",
    "output": "markdown"
  }
}
```

Compare against the baseline before/after the migration window to isolate the transfer traffic.

**2. CPU activity** (confirms the pod was active):

```json
metrics_read { "command": "query_range", "flags": { "query": "rate(container_cpu_usage_seconds_total{pod=\"<POD_NAME>\",namespace=\"<NS>\"}[1m])", "start": "<START>", "end": "<END>", "step": "30s", "output": "markdown" } }
```

**3. Pod logs** (transfer progress with bytes and elapsed time):

```json
debug_read { "command": "logs", "flags": { "name": "<POD_NAME>", "namespace": "<NS>", "tail": 200, "output": "markdown" } }
```

## Time Window for Completed Migrations

When querying metrics for a past migration, always compute the exact time window from plan metadata first:

1. Get the plan timestamps:

```json
mtv_read { "command": "describe plan", "flags": { "name": "<PLAN>", "namespace": "<NS>", "output": "markdown" } }
```

2. Use the start/completion timestamps as ISO-8601 `start`/`end` in `query_range`:

```json
metrics_read { "command": "query_range", "flags": { "query": "<PROMQL>", "start": "2025-06-15T10:00:00Z", "end": "2025-06-15T12:30:00Z", "step": "60s", "output": "markdown" } }
```

Do not use relative offsets like `-1h` for completed migrations -- the data may fall outside that window.

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

### Time parameters (`start` / `end`)

Accepted formats:
- Relative duration: `"-1h"`, `"-30m"`, `"-2d"`
- ISO-8601 string: `"2025-06-15T10:00:00Z"`

Integer Unix timestamps are NOT accepted. If you have a Unix timestamp, convert it to ISO-8601 first.

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

---

## Using Presets

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

Promote any instant preset to a range query by passing `start`:

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_migration_status", "start": "-2h", "step": "30s", "output": "markdown" } }
```

See the `metrics-query-cookbook` for the full preset catalog.

---

## PromQL Quick Reference

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
