# Installation

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** -- fast Python package manager
  (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Docker or Podman** -- used by `mtv-agent start` to run the three MCP
  server containers that give the agent access to your OpenShift cluster.
  Not required if you run the MCP servers yourself and use `mtv-agent serve`
  instead
- **An OpenShift cluster** with [MTV/Forklift](https://github.com/kubev2v/forklift)
  installed. You should have a valid kubeconfig (via `oc login` or `kubectl`)
  or a bearer token for the cluster API
- **An OpenAI-compatible LLM server** -- either
  [LM Studio](https://lmstudio.ai) (local) or
  [Claude](https://docs.anthropic.com/en/docs/claude-code) via the bundled
  proxy. See [llm-backends.md](llm-backends.md) for details.

## Install from pip

```bash
uv pip install mtv-agent
```

This installs the `mtv-agent` command along with all Python dependencies,
including `claude-openai-proxy`.

Verify the installation:

```bash
mtv-agent --version
```

## Install from source

For contributors or if you want to run from a git checkout:

```bash
git clone https://github.com/yaacov/mtv-agent.git
cd mtv-agent
uv sync --extra dev
```

`uv sync` creates the virtual environment automatically (in `.venv/`),
installs all dependencies, and sets up the package in editable mode.
Code changes take effect immediately.

## Initialise a workspace

After installing, run `init` to create a local workspace with the default
configuration, skills, and playbooks:

```bash
mtv-agent init
```

This creates `~/.mtv-agent/` with:

```
~/.mtv-agent/
├── config.json     # agent settings (LLM, server, MCP, memory, etc.)
├── skills/         # markdown reference guides the agent can load on demand
└── playbooks/      # task playbooks exposed in the web UI
```

You can edit any of these files to customise the agent's behaviour.

### Options

Initialise into a custom directory:

```bash
mtv-agent init --dir ./my-workspace
```

Reset an existing workspace back to defaults:

```bash
mtv-agent init --force
```

## What's next

Follow the [Quick Start](quickstart.md) guide to set up an LLM backend and
launch the agent.
