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
| `tsv` | Tab-separated values for data export. |
| `raw` | You need the full Prometheus API response as-is. |

**Always use `output: "markdown"` when presenting results to the user.**
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

See the `metrics-query-cookbook` for the full preset catalog and PromQL reference.
