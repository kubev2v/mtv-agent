# Quick Start

This guide walks you through going from a fresh install to a running
mtv-agent with the web UI -- in under five minutes.

## Before you begin

Make sure you have completed [Installation](installation.md):

```bash
pip install mtv-agent
mtv-agent init
```

You should also have:

- **Docker or Podman** installed -- `mtv-agent start` uses it to run the MCP
  server containers locally. If you run the MCP servers yourself, you can
  skip this and use `mtv-agent serve` instead.
- Access to an OpenShift cluster with MTV/Forklift (you need the API URL and
  a valid token)

## Step 1: Choose an LLM backend

mtv-agent needs an OpenAI-compatible LLM to power the conversation. Pick one:

### Option A: LM Studio (local, free)

1. Download and install [LM Studio](https://lmstudio.ai).
2. Open it, go to the **Discover** tab, and download a model. Recommended:
   - `Qwen2.5-Coder-32B-Instruct` -- best tool-calling accuracy
   - `Mistral-Small-24B-Instruct-2501` -- good balance of speed and quality
   - `Llama-3.1-8B-Instruct` -- lightweight, good for testing
3. Go to the **Developer** tab and click **Start Server**.

The server runs on `http://localhost:1234` by default, which is exactly what
mtv-agent expects. No config changes needed.

### Option B: Claude (cloud, requires Anthropic account)

1. Install the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
   and log in:

   ```bash
   claude
   ```

2. Verify it works:

   ```bash
   claude -p "hello"
   ```

The `claude-openai-proxy` that bridges Claude to an OpenAI-compatible API is
already installed as part of `mtv-agent`. You just need to pass `--with-cop`
when starting (see below).

For more details on either backend, see [LLM Backends](llm-backends.md).

## Step 2: Cluster credentials

The MCP server containers need access to your OpenShift cluster. mtv-agent
resolves credentials in this order:

1. **CLI flags** (`--kube-api-url`, `--kube-token`)
2. **Environment variables** (`KUBE_API_URL`, `KUBE_TOKEN`)
3. **Kubeconfig** (`~/.kube/config` or `$KUBECONFIG`)

### Easiest: use your existing kubeconfig

If you've already logged in with `oc login` or configured `kubectl`, you're
done -- mtv-agent reads the current context from your kubeconfig automatically.
Skip to Step 3.

### Alternative: set environment variables

```bash
export KUBE_API_URL=https://api.cluster.example.com:6443
export KUBE_TOKEN=$(oc whoami -t)
```

### Alternative: pass flags directly

```bash
mtv-agent start --kube-api-url https://api.cluster.example.com:6443 \
                --kube-token "$(oc whoami -t)"
```

### Specific kubeconfig file or context

```bash
mtv-agent start --kubeconfig ~/.kube/prod.config --kube-context prod-admin
```

## Step 3: Start the agent

### With LM Studio

```bash
mtv-agent start
```

### With Claude

```bash
mtv-agent start --with-cop
```

You should see output like:

```
INFO  Starting MCP servers (docker)...
INFO    mtv-agent-mcp-mtv -> http://localhost:8080/sse
INFO    mtv-agent-mcp-metrics -> http://localhost:8081/sse
INFO    mtv-agent-mcp-debug-queries -> http://localhost:8082/sse
INFO  Starting API server...
INFO  Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Open the web UI

Open your browser at:

```
http://localhost:8000
```

You'll see a chat interface where you can talk to the agent. Try asking:

- "List all migration plans"
- "Show me the VMware providers"
- "Check the cluster health"
- "What VMs are available for migration?"

The agent will use its MCP tools to query your cluster and respond with
real data.

## Stopping the agent

Press `Ctrl-C` in the terminal, or from another terminal run:

```bash
mtv-agent stop
```

This stops the MCP containers and the LLM proxy (if running).

## What's running

`mtv-agent start` manages five processes for you:

| Component | Port | Description |
|---|---|---|
| API server | 8000 | FastAPI app serving the chat API and web UI |
| kubectl-mtv MCP | 8080 | MTV/Forklift resource queries and mutations |
| kubectl-metrics MCP | 8081 | Prometheus/Thanos metric queries |
| kubectl-debug-queries MCP | 8082 | Kubernetes resources, logs, and events |
| claude-openai-proxy | 1234 | Claude-to-OpenAI adapter (only with `--with-cop`) |

## Customising

Edit `~/.mtv-agent/config.json` to change settings like the LLM endpoint, server
port, or memory limits. See the [README](../README.md#configuration) for the
full configuration reference.

Add your own skills to `~/.mtv-agent/skills/` or playbooks to
`~/.mtv-agent/playbooks/` to extend the agent's capabilities.

## Troubleshooting

**"Error: Kubernetes API URL not found"** or **"Error: Kubernetes token not found"**
The agent could not find cluster credentials. Make sure you've done one of:
(a) logged in with `oc login`, (b) exported `KUBE_API_URL` and `KUBE_TOKEN`,
or (c) passed `--kube-api-url` and `--kube-token`. If your kubeconfig uses
certificate-based auth instead of a bearer token, you'll need to use
environment variables or CLI flags with an explicit token.

**"Neither docker nor podman found in PATH"**
Install Docker or Podman. On macOS: `brew install podman`. On Fedora/RHEL:
`sudo dnf install podman`.

**"No models found at http://localhost:1234/v1"**
LM Studio is not running or no model is loaded. Open LM Studio, load a model,
and start the server from the Developer tab.

**Agent responds but doesn't use tools**
The MCP containers may not have started correctly. Check that the containers
are running: `docker ps` or `podman ps`. Verify your `KUBE_TOKEN` is still
valid: `oc whoami`.
