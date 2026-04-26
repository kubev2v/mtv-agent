# Quick Start

This guide walks you through going from a fresh install to a running
mtv-agent with the web UI -- in under five minutes.

## Before you begin

Make sure you have completed [Installation](installation.md):

```bash
uv tool install mtv-agent
mtv-agent init
```

> `uv tool install` keeps everything in an isolated venv and only places
> `mtv-agent` on your PATH. If you prefer pip, run `pip install mtv-agent`
> instead. See [Installation](installation.md) for details.

You should also have:

- **Docker or Podman** installed -- `mtv-agent start` uses it to run the MCP
  server containers locally. If you run the MCP servers yourself, you can
  skip this and use `mtv-agent serve` instead.
- Access to an OpenShift cluster with MTV/Forklift (you need the API URL and
  a valid token)

## Step 1: Choose an LLM backend

mtv-agent needs an OpenAI-compatible LLM to power the conversation. The
backend is selected by the `llm.type` field in `~/.mtv-agent/config.json`.

### Option A: Claude on Vertex AI (default)

The default configuration uses Claude via the bundled proxy. You just need
Google Cloud credentials:

1. Authenticate with Google Cloud:

   ```bash
   gcloud auth application-default login
   ```

2. Set the required environment variables:

   ```bash
   export CLOUD_ML_REGION=us-east5              # or your preferred region
   export ANTHROPIC_VERTEX_PROJECT_ID=my-project # your GCP project ID
   ```

No config changes needed -- `mtv-agent init` already sets `llm.type` to
`"claude-vertex"`.

### Option B: LM Studio (local, free)

1. Download and install [LM Studio](https://lmstudio.ai).
2. Open it, go to the **Discover** tab, and download a model. Recommended:
   - `Qwen2.5-Coder-32B-Instruct` -- best tool-calling accuracy
   - `Mistral-Small-24B-Instruct-2501` -- good balance of speed and quality
   - `Llama-3.1-8B-Instruct` -- lightweight, good for testing
3. Go to the **Developer** tab and click **Start Server**.

4. Edit `~/.mtv-agent/config.json` and set the LLM type to `"openai"`:

   ```json
   {
     "llm": {
       "type": "openai",
       "baseUrl": "http://localhost:1234/v1",
       "apiKey": "lm-studio",
       "model": null
     }
   }
   ```

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

See [CLI Reference](cli-reference.md) for the full list of flags and
credential resolution details.

## Step 3: Start the agent

### With Claude on Vertex AI (default)

```bash
CLOUD_ML_REGION=us-east5 ANTHROPIC_VERTEX_PROJECT_ID=my-project \
  mtv-agent start
```

### With LM Studio

```bash
mtv-agent start
```

You should see output similar to the following. The exact lines depend on
your `llm.type` setting -- the `claude-openai-proxy` line only appears when
`llm.type` is `"claude-vertex"` (the default); with `llm.type: "openai"`
(e.g. LM Studio) that line is absent:

```
INFO  Starting claude-openai-proxy on port 1234...   # claude-vertex only
INFO  Starting MCP servers (docker)...
INFO    mtv-agent-mcp-mtv -> http://localhost:8080/mcp
INFO    mtv-agent-mcp-metrics -> http://localhost:8081/mcp
INFO    mtv-agent-mcp-debug-queries -> http://localhost:8082/mcp
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

## Next steps

- [Configuration](configuration.md) -- customise the LLM endpoint, server
  port, memory limits, and MCP server URLs
- [Skills and Playbooks](skills-and-playbooks.md) -- extend the agent with
  custom reference guides and task workflows
- [Architecture](architecture.md) -- understand the components and data flow

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

**"claude-openai-proxy did not become ready"**
Make sure `CLOUD_ML_REGION` and `ANTHROPIC_VERTEX_PROJECT_ID` are set and
that you have run `gcloud auth application-default login`. Or switch to
a local model by setting `llm.type` to `"openai"` in config.json.

**"No models found at http://localhost:1234/v1"**
LM Studio is not running or no model is loaded. Open LM Studio, load a model,
and start the server from the Developer tab.

**Agent responds but doesn't use tools**
The MCP containers may not have started correctly. Check that the containers
are running: `docker ps` or `podman ps`. Verify your `KUBE_TOKEN` is still
valid: `oc whoami`.
