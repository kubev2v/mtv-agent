# kubectl-metrics MCP Server -- Known Issues

Tracking issues discovered during live migration testing (oVirt and VMware).
These affect the **kubectl-metrics MCP server binary**, not the mtv-agent repo.

## 1. Preset regex does not match migration pod names

**Affected presets**: `mtv_migration_pod_rx`, `mtv_migration_pod_tx`

The presets use regex patterns like `pod=~".*virt-v2v.*"` and `pod=~".*populator.*"`.
Actual migration pod names follow the pattern `{plan-name}-{vm-id}-{random}` (e.g.
`test-vmware-metrics-vm-43-tws62`), which does not match.

**Suggested fix**: Query by namespace instead of pod name regex, or use Forklift
labels (e.g. `plan`, `migration`) to select migration pods.

## 2. Populate pod regex mismatch

The populator regex `.*populator.*` does not match oVirt pods named `populate-*`
(e.g. `populate-c34c2a79-...`).

**Suggested fix**: Use `.*populat.*` to match both `populator-*` and `populate-*`.

## 3. Help examples use `output: "json"`

The `metrics_help` preset command returns examples with `output: "json"`. LLMs copy
the nearest example verbatim, overriding the system prompt and skill guidance to use
markdown.

**Suggested fix**: Change `output: "json"` to `output: "markdown"` in all help examples.

## 4. Missing populator CPU preset

There is no preset for monitoring oVirt/OpenStack populator pod activity via CPU
metrics. Since container-level network metrics may not be available for short-lived
populator pods (~under 60s), a CPU-based preset would provide a useful alternative.

**Suggested fix**: Add a `mtv_populator_cpu` preset using
`rate(container_cpu_usage_seconds_total{pod=~"populate.*"}[1m])`.
