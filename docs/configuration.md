# Configuration

mtv-agent settings are split into two JSON files:

- **`config.json`** -- agent and API server settings (LLM, server bind, skills,
  playbooks, memory, agent behaviour, cache)
- **`mcp.json`** -- MCP server definitions (URLs, container images, headers,
  Kubernetes auth)

After running `mtv-agent init`, both files are created at `~/.mtv-agent/`.

## File search order

The agent searches for each config file in this order:

1. `./config.json` (or `./mcp.json`) in the current working directory
2. `~/.mtv-agent/config.json` (or `~/.mtv-agent/mcp.json`)

You can also pass explicit paths with `--config` and `--mcp-config` on the
command line.

To print the built-in default config:

```bash
mtv-agent config
```

## `config.json`

```json
{
  "llm": {
    "type": "claude-vertex",
    "baseUrl": "http://localhost:1234/v1",
    "apiKey": "not-needed",
    "model": null
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "skills": { "dir": "~/.mtv-agent/skills", "maxActive": 3 },
  "playbooks": { "dir": "~/.mtv-agent/playbooks" },
  "memory": { "maxTurns": 20, "ttlSeconds": 3600, "toolResultLimit": 4000 },
  "agent": {
    "contextWindow": 30000,
    "maxIterations": 20,
    "maxRetries": 2,
    "retryDelay": 2.0,
    "llmTimeout": 360,
    "mcpToolTimeout": 360,
    "bashTimeout": 360
  },
  "cache": {
    "dir": "~/.mtv-agent/cache"
  }
}
```

### LLM settings (`llm`)

| Key | Default | Description |
|---|---|---|
| `type` | `claude-vertex` | Backend type: `"claude-vertex"` (auto-starts proxy) or `"openai"` (uses baseUrl directly) |
| `baseUrl` | `http://localhost:1234/v1` | OpenAI-compatible chat completion endpoint (ignored when type is `claude-vertex`) |
| `apiKey` | `not-needed` | API key sent in the `Authorization` header (ignored when type is `claude-vertex`) |
| `model` | `null` (auto-discovered) | Model name; when `null`, the agent queries `/v1/models` |

### Server settings (`server`)

| Key | Default | Description |
|---|---|---|
| `host` | `0.0.0.0` | API server bind address |
| `port` | `8000` | API server port |

### Skills settings (`skills`)

| Key | Default | Description |
|---|---|---|
| `dir` | `~/.mtv-agent/skills` | Directory containing skill definitions |
| `maxActive` | `3` | Maximum number of skills active simultaneously |

### Playbooks settings (`playbooks`)

| Key | Default | Description |
|---|---|---|
| `dir` | `~/.mtv-agent/playbooks` | Directory containing playbook files |

### Memory settings (`memory`)

| Key | Default | Description |
|---|---|---|
| `maxTurns` | `20` | Conversation turns kept per session |
| `ttlSeconds` | `3600` | Seconds before an idle session is evicted |
| `toolResultLimit` | `4000` | Maximum characters kept per tool result in history |

### Agent settings (`agent`)

| Key | Default | Description |
|---|---|---|
| `contextWindow` | `30000` | Default context window size (overridden if auto-detected from the LLM) |
| `maxIterations` | `20` | Maximum tool-loop iterations per request |
| `maxRetries` | `2` | LLM request retries on failure |
| `retryDelay` | `2.0` | Seconds between LLM retries |
| `llmTimeout` | `360` | LLM request timeout in seconds |
| `mcpToolTimeout` | `360` | MCP tool execution timeout in seconds |
| `bashTimeout` | `360` | Bash tool execution timeout in seconds |

### Cache settings (`cache`)

| Key | Default | Description |
|---|---|---|
| `dir` | `~/.mtv-agent/cache` | Directory for persistent caches (chat history, web cache) |

## `mcp.json`

```json
{
  "mcpServers": {
    "kubectl-mtv": {
      "url": "http://localhost:8080/mcp",
      "image": "quay.io/yaacov/kubectl-mtv-mcp-server:latest",
      "kubeAuth": true
    },
    "kubectl-metrics": {
      "url": "http://localhost:8081/mcp",
      "image": "quay.io/yaacov/kubectl-metrics-mcp-server:latest",
      "kubeAuth": true
    },
    "kubectl-debug-queries": {
      "url": "http://localhost:8082/mcp",
      "image": "quay.io/yaacov/kubectl-debug-queries-mcp-server:latest",
      "kubeAuth": true
    }
  }
}
```

### MCP server entry keys

| Key | Type | Default | Description |
|---|---|---|---|
| `url` | string | *(required)* | Streamable HTTP endpoint URL for the MCP server |
| `image` | string | | Container image used by `mtv-agent start` to run the server |
| `headers` | object | `{}` | Custom HTTP headers sent with every MCP request |
| `kubeAuth` | boolean | `false` | Inject auto-resolved Kubernetes credentials (`Authorization` and `X-Kubernetes-Server` headers) |

## Environment variable overrides

Every configuration value can be overridden by an environment variable. No
prefix is needed.

| Variable | Config key | Default | Description |
|---|---|---|---|
| `LLM_TYPE` | `llm.type` | `claude-vertex` | Backend type: `claude-vertex` or `openai` |
| `LLM_BASE_URL` | `llm.baseUrl` | `http://localhost:1234/v1` | OpenAI-compatible endpoint (ignored when type is `claude-vertex`) |
| `LLM_API_KEY` | `llm.apiKey` | `not-needed` | API key for the LLM server (ignored when type is `claude-vertex`) |
| `LLM_MODEL` | `llm.model` | auto-discovered | Model name (queries `/v1/models` if unset) |
| `SERVER_HOST` | `server.host` | `0.0.0.0` | API server bind address |
| `SERVER_PORT` | `server.port` | `8000` | API server port |
| `SKILLS_DIR` | `skills.dir` | bundled skills | Directory containing skill definitions |
| `PLAYBOOKS_DIR` | `playbooks.dir` | bundled playbooks | Directory containing playbooks |
| `MAX_ACTIVE_SKILLS` | `skills.maxActive` | `3` | Maximum skills active at once |
| `MEMORY_MAX_TURNS` | `memory.maxTurns` | `20` | Conversation turns kept per session |
| `MEMORY_TTL_SECONDS` | `memory.ttlSeconds` | `3600` | Seconds before a session is evicted |
| `CONTEXT_WINDOW` | `agent.contextWindow` | `30000` | Default context window (overridden if auto-detected) |
| `MAX_ITERATIONS` | `agent.maxIterations` | `20` | Maximum tool-loop iterations |
| `MAX_RETRIES` | `agent.maxRetries` | `2` | LLM request retries on failure |
| `RETRY_DELAY` | `agent.retryDelay` | `2.0` | Seconds between LLM retries |
| `LLM_TIMEOUT` | `agent.llmTimeout` | `360` | LLM request timeout in seconds |
| `MCP_TOOL_TIMEOUT` | `agent.mcpToolTimeout` | `360` | MCP tool execution timeout in seconds |
| `BASH_TIMEOUT` | `agent.bashTimeout` | `360` | Bash tool execution timeout in seconds |
| `MEMORY_TOOL_RESULT_LIMIT` | `memory.toolResultLimit` | `4000` | Max characters kept per tool result |
| `CACHE_DIR` | `cache.dir` | `~/.mtv-agent/cache` | Directory for persistent caches |
