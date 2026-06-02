---
name: troubleshoot-migration
category: Troubleshooting
description: >
  Diagnoses failed or stuck migrations by checking plan status, migration pods,
  container logs, events, provider connectivity, and cluster resources.
tools:
  - mtv_read (server: kubectl-mtv)
  - debug_read (server: kubectl-debug-queries)
  - metrics_read (server: kubectl-metrics)
---

# Troubleshoot Migration

Goal: systematically diagnose why a migration failed or is stuck, using plan status,
pod logs, events, and metrics.

## Inputs

Collect before starting:
- **namespace** -- check session context first; **ASK the user** only if missing.
- **plan name** -- resolved in step 1 (do NOT assume which plan).
- **symptom** (optional) -- **ASK the user** what they are seeing:
  - Plan stuck / not progressing
  - VM migration failed
  - Disk transfer stalled
  - Migration very slow
  - Other (describe)

## Notes

- The MTV operator namespace is usually `openshift-mtv` (shown as `<MTV_NAMESPACE>` below).
  If unsure, run `mtv_read { "command": "health", "flags": { "all_namespaces": true } }` first
  and note the namespace from the output.

## Steps

### Step 1 -- Identify the plan

```json
mtv_read { "command": "get plan", "flags": { "namespace": "<NAMESPACE>", "output": "markdown" } }
```

**IF only one plan exists**: use it and tell the user.
**IF multiple plans exist**: list them and **ASK the user** which one to troubleshoot.
**IF no plans exist**: tell the user no plans are found. Suggest checking the namespace.

### Step 2 -- Get plan details and VM status

```json
mtv_read { "command": "describe plan", "flags": { "name": "<PLAN_NAME>", "namespace": "<NAMESPACE>", "output": "markdown" } }
```

```json
mtv_read { "command": "get plan", "flags": { "name": "<PLAN_NAME>", "vms": true, "disk": true, "namespace": "<NAMESPACE>", "output": "markdown" } }
```

Identify:
- Overall plan status (Executing, Failed, Succeeded, etc.)
- Which VMs are stuck or failed
- Disk transfer progress (is it advancing?)

**IF plan status is Succeeded**: tell the user the plan completed successfully. No troubleshooting needed.
**IF plan status is Failed or VMs are failed**: continue to step 3.
**IF plan status is Executing but appears stuck**: continue to step 3.

### Step 3 -- Check plan and mapping conditions

```json
mtv_read { "command": "get plan", "flags": { "name": "<PLAN_NAME>", "namespace": "<NAMESPACE>", "output": "json" }, "fields": ["metadata", "status"] }
```

Look at `.status.conditions` for error or warning conditions. Common conditions:
- **Ready=False**: plan has configuration issues
- **HasCriticalCondition=True**: VMs have critical migration concerns
- **Executing=False with message**: plan stalled with a specific reason

Also check mapping conditions:

```json
debug_read { "command": "list", "flags": { "resource": "networkmaps", "namespace": "<NAMESPACE>", "output": "json", "query": "select name, status.conditions" } }
```

```json
debug_read { "command": "list", "flags": { "resource": "storagemaps", "namespace": "<NAMESPACE>", "output": "json", "query": "select name, status.conditions" } }
```

**IF conditions reveal the root cause**: skip to step 11 (report).
**IF conditions look normal**: continue to step 4 (logs).

### Step 4 -- Check MTV controller logs for the plan

```json
debug_read { "command": "logs", "flags": { "name": "deployment/forklift-controller", "namespace": "<MTV_NAMESPACE>", "container": "main", "tail": 200, "query": "where fields.plan ~= '.*<PLAN_NAME>.*' and level = 'ERROR'", "output": "markdown" } }
```

**IF errors found**: save them -- they often reveal the root cause (provider errors,
conversion failures, resource issues).
**IF no errors at error level**: try warning level:

```json
debug_read { "command": "logs", "flags": { "name": "deployment/forklift-controller", "namespace": "<MTV_NAMESPACE>", "container": "main", "tail": 200, "query": "where fields.plan ~= '.*<PLAN_NAME>.*' and level = 'WARN'", "output": "markdown" } }
```

### Step 5 -- Check migration pods in the target namespace

```json
debug_read { "command": "list", "flags": { "resource": "pods", "namespace": "<NAMESPACE>", "selector": "plan", "output": "markdown" } }
```

**IF pods found in error/pending/crash state**: get their logs:

```json
debug_read { "command": "logs", "flags": { "name": "<POD_NAME>", "namespace": "<NAMESPACE>", "tail": 200, "query": "where level = 'ERROR'", "output": "markdown" } }
```

For crashed pods, also check previous container:

```json
debug_read { "command": "logs", "flags": { "name": "<POD_NAME>", "namespace": "<NAMESPACE>", "previous": true, "tail": 200, "output": "markdown" } }
```

**IF no migration pods found**: the migration may not have started pod creation yet --
check events (step 6) and provider (step 7).

**IF pods are Running but not progressing**: check for OOMKilled or resource limits:

```json
debug_read { "command": "get", "flags": { "resource": "pod", "name": "<POD_NAME>", "namespace": "<NAMESPACE>", "output": "json" } }
```

Look for `.status.containerStatuses[*].lastState.terminated.reason` equal to `"OOMKilled"`.

### Step 6 -- Check events in the target namespace

```json
debug_read { "command": "events", "flags": { "namespace": "<NAMESPACE>", "query": "where type = 'Warning' order by lastTimestamp desc", "limit": 20, "output": "markdown" } }
```

**IF relevant events found**: save them. Common warning events during migration:
- **FailedScheduling**: cluster lacks resources for migration pods
- **FailedAttachVolume / FailedMount**: storage issues
- **BackOff / CrashLoopBackOff**: pod is crashing repeatedly
- **ProvisioningFailed**: PVC cannot be created (storage class issue)

### Step 7 -- Check provider connectivity

```json
mtv_read { "command": "get provider", "flags": { "namespace": "<NAMESPACE>", "output": "markdown" } }
```

**IF source provider is not Ready**: the provider lost connectivity.

```json
debug_read { "command": "events", "flags": { "namespace": "<NAMESPACE>", "resource": "Pod", "query": "where type = 'Warning'", "limit": 10, "output": "markdown" } }
```

### Step 8 -- Check cluster resource pressure

```json
debug_read { "command": "list", "flags": { "resource": "nodes", "output": "markdown" } }
```

```json
metrics_read { "command": "query", "flags": { "query": "(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100", "output": "markdown" } }
```

**IF any node is NotReady or memory > 90%**: cluster resource pressure may be causing
scheduling failures for migration pods.

### Step 9 -- Check storage (PVC status)

```json
debug_read { "command": "list", "flags": { "resource": "pvc", "namespace": "<NAMESPACE>", "query": "where status.phase != 'Bound'", "output": "markdown" } }
```

**IF unbound PVCs found**: storage provisioning is failing.

Check for a default StorageClass:

```json
debug_read { "command": "list", "flags": { "resource": "storageclasses", "output": "markdown" } }
```

**IF no default StorageClass**: this is likely the root cause -- DataVolumes require a default.

### Step 10 -- Check migration throughput (if migration is slow)

Only run if the symptom is "slow migration":

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_net_throughput", "output": "markdown" } }
```

```json
metrics_read { "command": "preset", "flags": { "name": "mtv_storage_throughput", "output": "markdown" } }
```

**IF throughput is very low** (< 1 MB/s): possible network bottleneck, storage I/O issue,
or throttling. Check:

```json
metrics_read { "command": "preset", "flags": { "name": "namespace_network_errors", "output": "markdown" } }
```

### Step 11 -- Report

Present findings organized by category:

**Plan Status**
- Plan name, status, VM progress

**Root Cause Analysis** (based on what was found):

| Symptom | Likely Cause | Evidence | Remediation |
|---------|-------------|----------|-------------|
| Condition errors | Plan/mapping misconfiguration | Conditions from step 3 | Fix plan or mapping configuration |
| Pod CrashLoopBackOff | Converter failed | Log errors from step 5 | Check source VM compatibility, increase memory limits |
| Pod OOMKilled | Insufficient memory for converter | OOMKilled in pod status | Increase converter memory via `settings set` |
| PVC Pending | No default StorageClass | Unbound PVCs from step 9 | Set a default StorageClass |
| FailedScheduling | Cluster out of resources | Events from step 6, node memory from step 8 | Free resources or scale cluster |
| Provider not Ready | Lost connectivity to source | Provider status from step 7 | Check credentials, network, TLS |
| Low throughput | Network/storage bottleneck | Throughput metrics from step 10 | Check network path, storage IOPS |
| No migration pods | Plan not progressing | Empty pod list from step 5 | Check controller logs from step 4 |

**Recommended Actions**:
- List specific actions the user should take based on the findings
- Reference other playbooks if relevant (e.g., `check-mtv-health`, `check-cluster-health`)
