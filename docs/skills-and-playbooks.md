# Skills and Playbooks

mtv-agent ships with two kinds of markdown content that extend the agent's
knowledge and guide its behaviour: **skills** and **playbooks**.

## Overview

| | Skills | Playbooks |
|---|---|---|
| **Purpose** | Reference knowledge loaded on demand | Task workflows exposed in the web UI |
| **Loaded by** | The LLM calling the `select_skill` tool | The user selecting a playbook in the sidebar |
| **Effect** | Skill body is injected into the system prompt | Playbook body is sent as the initial user message |
| **Location** | `~/.mtv-agent/skills/<name>/SKILL.md` | `~/.mtv-agent/playbooks/<name>.md` |
| **Limit** | Up to `maxActive` (default 3) at once | One per conversation |

## How skills work

Skills are markdown reference guides that the agent loads on demand during a
conversation. Each skill has a name, a short description, and a body.

When the agent determines it needs specialised knowledge (for example, how to
query vSphere inventory fields), it calls the `select_skill` virtual tool.
The skill's body is then injected into the system prompt so the LLM can
reference it in subsequent turns.

The agent sees a catalog of all available skills (name + description) in its
system prompt and decides which to activate based on the user's question.

### Bundled skills

| Skill | Description |
|---|---|
| `inventory-tool-guide` | TSL query syntax, pitfalls, resource matrix, and mapping workflow |
| `inventory-vsphere` | vSphere VM, network, datastore, host, cluster, and folder field reference |
| `inventory-ovirt` | oVirt/RHV inventory field reference and query examples |
| `inventory-openstack` | OpenStack inventory field reference and query examples |
| `inventory-openshift` | OpenShift inventory field reference |
| `inventory-ova` | OVA inventory field reference |
| `inventory-ec2` | Amazon EC2 inventory field reference |
| `inventory-hyperv` | Hyper-V inventory field reference |
| `metrics-tool-guide` | How to use `metrics_read` and `metrics_help`, output rules, PromQL |
| `metrics-query-cookbook` | Preset queries, Ceph/network/pod/MTV metric tables |
| `mtv-cli-docs` | Links to the kubectl-mtv HTML guide and MCP-to-CLI translation |
| `mtv-docs` | Red Hat MTV 2.11 documentation deep links |

## How playbooks work

Playbooks are task-oriented markdown files that appear in the web UI sidebar.
When a user selects a playbook, its body is sent as the initial chat message,
guiding the agent through a multi-step workflow.

Playbooks typically include:

- A goal statement
- Required inputs (e.g. namespace, provider name)
- Step-by-step instructions with example tool calls
- Expected output format

### Bundled playbooks

| Playbook | Category | Description |
|---|---|---|
| `browse-source-vms` | Inventory | List providers, query VM inventory, report concerns |
| `check-cluster-health` | Health | Ceph storage, node memory, pod restarts, problem pods |
| `check-mtv-health` | Health | Forklift health, pods, logs, and events |
| `configure-vddk-image` | Setup | Get, set, or unset the global VDDK image setting |
| `create-migration-target` | Setup | Create an OpenShift host provider and verify |
| `create-vsphere-provider` | Setup | Credentials, optional VDDK, create vSphere provider |
| `migration-status-report` | Migration | Metrics-based report over a timespan; drill into failures |
| `monitor-migration-plan` | Migration | VM/disk progress, throughput, pod traffic |
| `show-migration-network-traffic` | Migration | RX/TX per migration pod, errors, fallbacks |
| `troubleshoot-migration` | Migration | End-to-end diagnosis for failed or stuck plans |

## Directory layout

After `mtv-agent init`, the workspace looks like:

```
~/.mtv-agent/
├── skills/
│   ├── inventory-tool-guide/
│   │   └── SKILL.md
│   ├── inventory-vsphere/
│   │   └── SKILL.md
│   ├── metrics-tool-guide/
│   │   └── SKILL.md
│   └── ...
└── playbooks/
    ├── browse-source-vms.md
    ├── check-cluster-health.md
    ├── monitor-migration-plan.md
    └── ...
```

Skills live in subdirectories (`<name>/SKILL.md`). Playbooks are flat files
(`<name>.md`).

## Authoring a custom skill

Create a new directory under your skills folder with a `SKILL.md` file:

```bash
mkdir -p ~/.mtv-agent/skills/my-custom-skill
```

Write the file with YAML frontmatter and a markdown body:

```markdown
---
name: my-custom-skill
description: Short description shown in the agent's skill catalog.
---

# My Custom Skill

Detailed reference content goes here. The agent will see this text
when it activates the skill.

## Section One

- Use tables, code blocks, and examples
- The agent uses this as context for answering questions
```

**Frontmatter fields:**

| Field | Required | Description |
|---|---|---|
| `name` | yes | Unique skill name (used in `select_skill` calls) |
| `description` | yes | One-line summary shown in the skill catalog |

The body can be any length, but keep in mind that it is injected into the
system prompt and counts against the context window.

## Authoring a custom playbook

Create a markdown file in the playbooks directory:

```markdown
---
name: my-custom-playbook
category: Custom
description: >
  One-line description shown in the web UI sidebar.
tools:
  - mtv_read (server: kubectl-mtv)
  - debug_read (server: kubectl-debug-queries)
skills:
  - inventory-tool-guide
---

# My Custom Playbook

Goal: describe what this playbook accomplishes.

## Inputs

- `namespace` (required): the target namespace

## Steps

### Step 1: Gather information

Use `mtv_read` to list providers:

    {"command": "get provider", "flags": "--namespace <namespace>"}

### Step 2: Analyse results

Summarise findings in a markdown table.
```

**Frontmatter fields:**

| Field | Required | Description |
|---|---|---|
| `name` | yes | Unique playbook name (defaults to the filename without extension) |
| `category` | no | Group label shown in the web UI (default: `General`) |
| `description` | yes | Summary shown in the UI sidebar |
| `tools` | no | List of tools the playbook uses (informational) |
| `skills` | no | Skills to auto-activate when this playbook runs |

## Customising directories

By default, skills and playbooks are loaded from `~/.mtv-agent/skills/` and
`~/.mtv-agent/playbooks/`. You can change these paths in
[config.json](configuration.md) or via environment variables:

```bash
export SKILLS_DIR=/path/to/my/skills
export PLAYBOOKS_DIR=/path/to/my/playbooks
```

Or in `config.json`:

```json
{
  "skills": { "dir": "/path/to/my/skills", "maxActive": 3 },
  "playbooks": { "dir": "/path/to/my/playbooks" }
}
```
