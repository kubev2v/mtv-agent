# CLI Reference

The `mtv-agent` command is the main entry point. It is installed automatically
with `pip install mtv-agent` and can also be invoked as `python -m mtv_agent`.

## Synopsis

```
mtv-agent init   [--dir DIR] [--force]
mtv-agent start  [OPTIONS]
mtv-agent serve  [OPTIONS]
mtv-agent stop
mtv-agent config
mtv-agent --version
```

## Subcommands

### `mtv-agent init`

Create a workspace with default configuration, skills, and playbooks.

```bash
mtv-agent init              # creates ~/.mtv-agent/
mtv-agent init --dir ./ws   # custom directory
mtv-agent init --force      # overwrite existing files
```

| Flag | Description |
|---|---|
| `--dir DIR` | Workspace directory (default: `~/.mtv-agent`) |
| `--force` | Overwrite existing config, skills, and playbooks |

### `mtv-agent start`

Start the MCP server containers, optional LLM proxy, and the API server.

```bash
mtv-agent start
mtv-agent start --with-cop
mtv-agent start --runtime podman --port 9000
mtv-agent start --open
```

| Flag | Description |
|---|---|
| `--with-cop` | Start `claude-openai-proxy` alongside the agent |
| `--runtime docker\|podman` | Container runtime (auto-detected if omitted) |
| `--host HOST` | API server bind address (default: `0.0.0.0`) |
| `--port PORT` | API server port (default: `8000`) |
| `--config PATH` | Path to `config.json` |
| `--mcp-config PATH` | Path to `mcp.json` |
| `--no-web` | Do not serve the web UI |
| `--open` | Open the web UI in a browser when the server is ready (skipped with `--no-web`) |
| `--skip-tls` | Skip TLS verification for Kubernetes API |
| `--kube-api-url URL` | Kubernetes API URL (overrides kubeconfig) |
| `--kube-token TOKEN` | Kubernetes bearer token (overrides kubeconfig) |
| `--kubeconfig PATH` | Path to kubeconfig file |
| `--kube-context NAME` | Kubeconfig context to use |

### `mtv-agent serve`

Start only the API server. MCP servers and the LLM backend must already be
running externally.

```bash
mtv-agent serve
mtv-agent serve --host 127.0.0.1 --port 9000
mtv-agent serve --open
```

| Flag | Description |
|---|---|
| `--host HOST` | API server bind address (default: `0.0.0.0`) |
| `--port PORT` | API server port (default: `8000`) |
| `--config PATH` | Path to `config.json` |
| `--mcp-config PATH` | Path to `mcp.json` |
| `--no-web` | Do not serve the web UI |
| `--open` | Open the web UI in a browser when the server is ready (skipped with `--no-web`) |
| `--skip-tls` | Skip TLS verification for Kubernetes API |
| `--kube-api-url URL` | Kubernetes API URL (overrides kubeconfig) |
| `--kube-token TOKEN` | Kubernetes bearer token (overrides kubeconfig) |
| `--kubeconfig PATH` | Path to kubeconfig file |
| `--kube-context NAME` | Kubeconfig context to use |

### `mtv-agent stop`

Stop MCP containers and the `claude-openai-proxy` process (if running).

```bash
mtv-agent stop
```

### `mtv-agent config`

Print the default `config.json` to stdout. Useful for piping or inspection.

```bash
mtv-agent config
mtv-agent config > ~/.mtv-agent/config.json
```

## Cluster credential resolution

The `start` and `serve` commands need a Kubernetes API URL and bearer token
(passed to MCP containers or used for header injection). Credentials are
resolved in priority order:

1. **CLI flags** -- `--kube-api-url` and `--kube-token`
2. **Environment variables** -- `KUBE_API_URL` and `KUBE_TOKEN`
3. **Kubeconfig** -- the current context from `~/.kube/config` (or `$KUBECONFIG`)

Use `--kubeconfig` to point at a specific file, and `--kube-context` to select
a context other than the current one.

If you have logged in with `oc login` or configured `kubectl`, no flags or
environment variables are needed -- the agent picks up credentials from your
kubeconfig automatically.

> **Note:** A valid bearer token is required. Kubeconfig entries that use only
> certificate-based authentication will not work with the MCP containers. In
> that case, use environment variables or CLI flags with an explicit token.
