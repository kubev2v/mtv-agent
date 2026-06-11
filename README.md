# mtv-agent

AI agent for **MTV / Forklift** virtual machine migrations with a FastAPI server and a Textual TUI client.

## Install

```bash
uv tool install mtv-agent
```

Or for development:

```bash
git clone https://github.com/kubev2v/mtv-agent.git
cd mtv-agent
uv sync
```

## Prerequisites

mtv-agent relies on three kubectl/oc plugins that provide MCP servers for cluster interaction. Install them before running the agent.

### kubectl-mtv (`oc mtv`)

Manages Forklift migrations — providers, plans, mappings, inventory, and health checks.

```bash
curl -sSL https://raw.githubusercontent.com/yaacov/kubectl-mtv/main/install.sh | bash
```

Or build from source — see [yaacov/kubectl-mtv](https://github.com/yaacov/kubectl-mtv).

### kubectl-metrics (`oc metrics`)

Queries Prometheus / Thanos metrics on OpenShift clusters.

```bash
curl -sSL https://raw.githubusercontent.com/yaacov/kubectl-metrics/main/install.sh | bash
```

Or build from source — see [yaacov/kubectl-metrics](https://github.com/yaacov/kubectl-metrics).

### kubectl-debug-queries (`oc debug-queries`)

Queries Kubernetes resources, logs, and events using an SQL-like language.

```bash
curl -sSL https://raw.githubusercontent.com/yaacov/kubectl-debug-queries/main/install.sh | bash
```

Or build from source — see [yaacov/kubectl-debug-queries](https://github.com/yaacov/kubectl-debug-queries).

All three install to `~/.local/bin` by default. Verify with:

```bash
oc mtv --help
oc metrics --help
oc debug-queries --help
```

## Quick Start

```bash
# Bootstrap ~/.mtv-agent/ with config files
mtv-agent init

# Edit config (LLM endpoint, MCP servers, etc.)
vim ~/.mtv-agent/config.json
vim ~/.mtv-agent/mcp.json

# Run everything in one command (server + TUI)
mtv-agent
```

This starts the server in the background and launches the TUI. Server logs go to `~/.mtv-agent/server.log`. On exit the server shuts down automatically.

To run server and TUI separately (e.g. for development):

```bash
# Terminal 1: start the server
mtv-server

# Terminal 2: start the TUI
mtv-tui
```

When running from a dev checkout with `uv run`:

```bash
uv run mtv-agent       # combined
uv run mtv-server      # server only
uv run mtv-tui         # TUI only
```

## CLI

### `mtv-agent`

| Subcommand | Description |
|------------|-------------|
| *(default)* / `run [--resume ID]` | Start the server + TUI (optionally resume a saved session) |
| `run --dump-http` | Dump LLM HTTP requests/responses to `~/.mtv-agent/dumps/` |
| `run --dump-http-dir DIR` | Set dump directory (implies `--dump-http`) |
| `init [--dir DIR] [--force]` | Bootstrap `~/.mtv-agent/` with config, skills, and commands |
| `config` | Print default `config.json` to stdout |

### `mtv-server`

Starts the API server directly (no TUI). Used for development or headless deployments.

### `mtv-tui`

Starts only the TUI client, connecting to an already-running server. Accepts `--resume <id>` to resume a saved chat session on startup.

## Configuration

Both `config.json` and `mcp.json` are **required**. The server exits with a helpful error if either is missing, telling you to run `mtv-agent init`.

Config files are searched in order: `./` (CWD) then `~/.mtv-agent/`.

### `config.json`

```json
{
  "llm": {
    "baseUrl": "http://localhost:1234/v1",
    "apiKey": "not-needed",
    "model": null
  },
  "server": { "host": "0.0.0.0", "port": 8000 },
  "skills":   { "dir": "~/.mtv-agent/skills" },
  "commands": { "dir": "~/.mtv-agent/commands" },
  "cache":    { "dir": "~/.mtv-agent/cache" },
  "agent":    { "maxIterations": 20 },
  "debug":    { "dumpHttp": false, "dumpHttpDir": "~/.mtv-agent/dumps" }
}
```

Set `model` to `null` for auto-discovery from the LLM endpoint.

### `mcp.json`

Defines external MCP servers. Both `stdio` and `http` transports are supported:

```json
{
  "mcpServers": {
    "kubectl-mtv": {
      "transport": "stdio",
      "command": "oc",
      "args": ["mtv", "mcp-server"]
    },
    "kubectl-metrics": {
      "transport": "stdio",
      "command": "oc",
      "args": ["metrics", "mcp-server", "--insecure-skip-tls-verify"]
    }
  }
}
```

### Data file lookup

Skills and commands directories are set in `config.json` via `skills.dir` and `commands.dir`. After running `mtv-agent init`, the config points to `~/.mtv-agent/skills/` and `~/.mtv-agent/commands/`.

### Error handling

The server validates configuration at startup and exits with clear guidance on failure:

- **Missing config/mcp files** — lists the searched paths and suggests `mtv-agent init`
- **MCP connection failure** — lists each failed server with its connection details and troubleshooting hints

## API

| Method   | Path                         | Purpose                                    |
|----------|------------------------------|--------------------------------------------|
| `GET`    | `/api/status`                | Model name, server count, tool count       |
| `GET`    | `/api/mcp`                   | All servers, tools, and policies           |
| `PUT`    | `/api/mcp`                   | Update tool policies (persisted to disk)   |
| `GET`    | `/api/commands`              | List available slash commands              |
| `POST`   | `/api/chat`                  | Streaming SSE chat                         |
| `POST`   | `/api/chat/{id}/cancel`      | Cancel active stream                       |
| `POST`   | `/api/chat/{id}/approve`     | Approve/reject a pending tool call         |
| `GET`    | `/api/chats`                 | List saved chats                           |
| `GET`    | `/api/chats/{id}`            | Get chat detail                            |
| `DELETE` | `/api/chats/{id}`            | Delete a chat                              |

### SSE Events

| Event          | Data                            | Notes                                |
|----------------|---------------------------------|--------------------------------------|
| `session`      | `{session_id}`                  | First event, establishes session     |
| `thinking`     | `{}`                            | LLM is processing                    |
| `tool_call`    | `{name, arguments, pending}`    | `pending: true` = waiting for approval |
| `tool_result`  | `{name, result}`                | Tool completed                       |
| `tool_rejected`| `{name, reason}`                | Tool rejected by policy or user      |
| `content`      | `{content}`                     | Final assistant response             |
| `error`        | `{message}`                     | Error occurred                       |

## Tool Policies

Policies control whether tools run automatically, require approval, or are blocked.

**Default policy is `ask`** — all external MCP tools require approval unless overridden. Skills are auto-accepted (read-only reference data).

Resolution order:
1. Per-tool override (`policy.tools.{tool_name}`)
2. Bash prefix matching (for the bash server only)
3. Server default (`policy.default`)
4. Global default (`default_policy`)

The **bash** server adds prefix matching — commands starting with `ls`, `cat`, `kubectl get`, etc. are auto-accepted; `rm -rf`, `shutdown`, etc. are rejected; everything else requires approval.

**Managing policies from the TUI:**
- When prompted for tool approval, choose **Always Accept** or **Always Reject** to set a persistent per-tool policy (or per-prefix for bash)
- `/policy` — view all current policies and per-tool overrides
- `/policy reset` — restore all policies to defaults

## Commands

Commands are markdown files in the `commands/` data directory that provide step-by-step instructions for common tasks. Each is exposed as a TUI slash command.

| Command | Description |
|---------|-------------|
| `/browse-source-vms` | Browse VMs available for migration |
| `/check-cluster-health` | Check Ceph, storage, memory, pods |
| `/check-mtv-health` | Check MTV/Forklift operator health |
| `/configure-vddk-image` | Manage VDDK image settings |
| `/create-migration-target` | Create OpenShift target provider |
| `/create-vsphere-provider` | Create vSphere source provider |
| `/migration-status-report` | Report on all migrations |
| `/monitor-migration-plan` | Monitor a specific migration plan |
| `/show-migration-network-traffic` | Show per-pod network transfer rates |
| `/troubleshoot-migration` | Diagnose failed or stuck migrations |

Usage: `/command-name [optional context]`

```
> /check-mtv-health
> /browse-source-vms show powered-on VMs from my vsphere provider
```

## TUI Commands

| Command | Action |
|---------|--------|
| `/help` | List all commands |
| `/ns <name\|--all>` | Set namespace (injected into tool calls) |
| `/clear` | Clear chat and reset session |
| `/id` | Show current session ID |
| `/resume <id>` | Resume a saved chat session |
| `/status` | Refresh status bar |
| `/history` | Show saved chats |
| `/policy` | View current tool policies |
| `/policy reset` | Reset policies to defaults |
| `!cmd` | Run a shell command directly |
| `Ctrl+L` | Clear screen |
| `Ctrl+C` | Quit |
| `↑` / `↓` | Navigate prompt history |

On exit, the session ID and a `--resume` command are printed to the terminal for easy copy-paste.

Chat history (including tool calls and results) is saved to `~/.mtv-agent/cache/` and fully restored on resume, so the LLM retains context from prior tool interactions.

## Development

```bash
# Install dependencies
uv sync

# Format
uv run ruff format .

# Lint
uv run ruff check .

# Run tests
uv run pytest tests/
```
