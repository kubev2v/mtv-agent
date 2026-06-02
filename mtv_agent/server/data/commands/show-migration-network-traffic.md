---
name: show-migration-network-traffic
category: Migration
description: >
  Shows per-pod inbound (RX) and outbound (TX) network transfer rates
  during VM migration, plus any network errors or drops.
tools:
  - metrics_read (server: kubectl-metrics)
  - mtv_read (server: kubectl-mtv)
  - debug_read (server: kubectl-debug-queries)
---

# Show Migration Network Traffic

Goal: show how much network bandwidth each migration pod is using,
detect errors, and present RX/TX tables.

This playbook focuses on **network traffic of migration pods** (virt-v2v, populator,
importer). For overall migration progress, use `monitor-migration-plan` instead.

## Inputs

Collect before starting:
- **namespace** -- check session context first; **ASK the user** only if missing.
  Suggest common values: `openshift-mtv`, `konveyor-forklift`.
- **migration plan** (optional) -- if the user mentions a specific migration or plan,
  **ASK for the plan name** so we can scope the time window. If the user just wants
  current traffic, no plan name is needed.

## Steps

### Step 1 -- Discover migration pods

List migration pods in the namespace to learn their actual names.

VMware/general migration pods (carry a `plan` label):

```json
debug_read { "command": "list", "flags": { "resource": "pods", "namespace": "<NAMESPACE>", "selector": "plan", "output": "markdown" } }
```

oVirt/OpenStack populator pods (named `populate-{uuid}-...`):

```json
debug_read { "command": "list", "flags": { "resource": "pods", "namespace": "<NAMESPACE>", "query": "where name ~= '^populate-'", "output": "markdown" } }
```

**IF pods found**: save the pod names and note the pod type (virt-v2v converter, populator,
importer). Also note the node each pod runs on (`spec.nodeName`) -- this is needed if
container-level network metrics are missing (see step 5a).

**IF no pods found**: there are no active migration pods. The migration may have completed
or not started. Continue to step 2 to check the time window from the plan.

### Step 2 -- Determine time window

**IF a specific migration plan was provided**:

```json
mtv_read { "command": "describe plan", "flags": { "name": "<PLAN_NAME>", "namespace": "<NAMESPACE>", "output": "markdown" } }
```

Look for start and completion timestamps. If not visible, fall back to:

```json
mtv_read { "command": "get plan", "flags": { "name": "<PLAN_NAME>", "namespace": "<NAMESPACE>", "output": "json" } }
```

Check `.status.migration.started` and `.status.migration.completed` fields.
Compute the migration duration and round up to the nearest Prometheus duration unit.
Save this as `<RATE_WINDOW>`.

Example: if `started = "2025-06-15T10:00:00Z"` and `completed = "2025-06-15T12:30:00Z"`,
the duration is 2.5 hours -- use `[3h]`. If 45 minutes, use `[1h]`.
If the migration is still running, use the time elapsed since start, rounded up.
If you cannot determine timestamps, fall back to `[1h]` as a safe default.

**IF FAIL** (plan not found): tell the user the plan was not found and **ASK** them
to verify the name and namespace. Stop here until clarified.

**IF no specific migration was given**: use a default rate window of `[1h]`.

### Step 3 -- Get inbound (RX) traffic by pod

Use the pod names from step 1 to build a regex filter (`<PODS>` = `pod1|pod2|...`).
If no pods were discovered (completed migration), query by namespace only.

```json
metrics_read { "command": "query", "flags": { "query": "topk(10, sort_desc(sum by (pod)(rate(container_network_receive_bytes_total{namespace=\"<NAMESPACE>\",pod=~\"<PODS>\"}[<RATE_WINDOW>]))))", "output": "markdown" } }
```

**IF data returned**: save the per-pod RX rates.
**IF no data**: no network traffic found. Possible causes:
- No pods running in the namespace
- Metrics not being collected
- Migration has not started yet

Note this and continue to step 4 (TX may still have data).

### Step 4 -- Get outbound (TX) traffic by pod

```json
metrics_read { "command": "query", "flags": { "query": "topk(10, sort_desc(sum by (pod)(rate(container_network_transmit_bytes_total{namespace=\"<NAMESPACE>\",pod=~\"<PODS>\"}[<RATE_WINDOW>]))))", "output": "markdown" } }
```

**IF data returned**: save the per-pod TX rates.
**IF no data**: note as above.

### Step 5 -- Check for network errors and drops

```json
metrics_read { "command": "preset", "flags": { "name": "namespace_network_errors", "output": "markdown" } }
```

**IF errors or drops found**: save them and flag the affected namespace/pod.
**IF no errors**: note that the network is clean.

### Step 5a -- Short-lived pod fallback (conditional)

Run this step if steps 3-4 returned no container-level network data for pods that
were active (confirmed by CPU metrics or pod logs). Short-lived pods (~under 60 seconds,
such as oVirt/OpenStack populator pods) may complete before cadvisor establishes
network namespace tracking. CPU and memory metrics are unaffected.

Use the node name from step 1 to query node-level network RX and TX during the migration window:

```json
metrics_read {
  "command": "query_range",
  "flags": {
    "query": [
      "instance:node_network_receive_bytes_excluding_lo:rate1m{instance=~\"<NODE_NAME>.*\"}",
      "instance:node_network_transmit_bytes_excluding_lo:rate1m{instance=~\"<NODE_NAME>.*\"}"
    ],
    "name": ["node_rx", "node_tx"],
    "start": "<MIGRATION_START>",
    "end": "<MIGRATION_END>",
    "step": "30s",
    "output": "markdown"
  }
}
```

Compare against baseline traffic before/after the migration window to isolate the transfer.

Also check CPU activity to confirm the pod was active:

```json
metrics_read { "command": "query_range", "flags": { "query": "rate(container_cpu_usage_seconds_total{pod=\"<POD_NAME>\",namespace=\"<NAMESPACE>\"}[1m])", "start": "<MIGRATION_START>", "end": "<MIGRATION_END>", "step": "30s", "output": "markdown" } }
```

**IF node-level data shows a clear spike**: include it in the report as "Node-level network
traffic (node: <NODE_NAME>)". Note that this includes all traffic on the node.
**IF no spike visible**: the transfer may have been too small or too fast to register. Note
this in the report.

### Step 6 -- Check migration pod health (conditional)

Run this step only if steps 3-4 returned no traffic data or show zero traffic
for pods that should be active.

```json
debug_read { "command": "list", "flags": { "resource": "pods", "namespace": "<NAMESPACE>", "selector": "plan", "output": "markdown" } }
```

**IF pods are in error/pending state**: get their events:

```json
debug_read { "command": "events", "flags": { "namespace": "<NAMESPACE>", "query": "where type = 'Warning'", "limit": 10, "output": "markdown" } }
```

**IF no migration pods found at all**: tell the user there are no active migration pods
in this namespace. The migration may have completed or not started.

### Step 7 -- Report

State the time window used (e.g. "Rate over last 1 hour" or
"Rate over migration window: 14:00-16:30 UTC").

Convert all byte rates to human-readable units (KB/s, MB/s, GB/s).

Present two tables:

**Inbound Traffic (RX)**

| Pod | Rate |
|-----|------|
| ... | ...  |

**Outbound Traffic (TX)**

| Pod | Rate |
|-----|------|
| ... | ...  |

**IF node-level metrics were used (step 5a)**: add a "Node-Level Network Traffic" section
showing the node RX/TX rates during the migration window, noting the baseline comparison.

**IF network errors or drops were found (step 5)**: add a "Network Warnings" section
listing the affected pods and error counts.

**IF migration pods are unhealthy (step 6)**: add a "Pod Issues" section listing
the pod statuses and events, with suggested remediation.

**IF no traffic at all and no migration pods**: tell the user no migration activity
was detected in this namespace. Suggest verifying the namespace and that a migration
is actually running.
