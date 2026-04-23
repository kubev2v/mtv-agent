# Architecture

mtv-agent is composed of a FastAPI backend, a web UI, an LLM backend, and one
or more MCP (Model Context Protocol) servers that provide cluster access tools.

## Components

`mtv-agent start` manages up to five processes:

| Component | Port | Description |
|---|---|---|
| API server | 8000 | FastAPI app serving the chat API and web UI |
| kubectl-mtv MCP | 8080 | MTV/Forklift resource queries and mutations |
| kubectl-metrics MCP | 8081 | Prometheus/Thanos metric queries |
| kubectl-debug-queries MCP | 8082 | Kubernetes resources, logs, and events |
| claude-openai-proxy | 1234 | Claude-to-OpenAI adapter (only with `--with-cop`) |

The three MCP containers are started and stopped automatically by the `start`
and `stop` commands. If you run MCP servers yourself, configure their URLs in
`mcp.json` and use `mtv-agent serve` instead.

## Data flow

```
┌──────────┐    HTTP/SSE    ┌──────────────┐   OpenAI API   ┌─────────────┐
│  Web UI  │ ◄────────────► │  API Server  │ ◄────────────► │ LLM Backend │
│ (browser)│                │  (FastAPI)   │                │(LM Studio / │
└──────────┘                └──────┬───────┘                │   Claude)   │
                                   │                        └─────────────┘
                          MCP HTTP │
                    ┌──────────────┼──────────────┐
                    │              │              │
               ┌────▼────┐  ┌─────▼─────┐  ┌────▼────────┐
               │  mtv     │  │  metrics  │  │  debug      │
               │  MCP     │  │  MCP      │  │  queries    │
               └────┬─────┘  └─────┬─────┘  │  MCP        │
                    │              │         └──────┬──────┘
                    └──────────────┼────────────────┘
                                   │
                          Kubernetes API
                                   │
                          ┌────────▼────────┐
                          │ OpenShift Cluster│
                          │ (MTV / Forklift) │
                          └─────────────────┘
```

1. The **web UI** sends chat messages to the API server over HTTP (or SSE for
   streaming).
2. The **API server** forwards the message to the **LLM backend** via the
   OpenAI chat completion API.
3. The LLM responds with text and/or **tool calls**.
4. The API server executes tool calls by routing them to the appropriate
   **MCP server** (or to built-in tools like bash and web fetch).
5. Tool results are fed back to the LLM, which may issue more tool calls or
   produce a final response.
6. This **tool loop** repeats until the LLM produces a final text response or
   the iteration limit is reached.

## Agent tool loop

The core loop in `agent.py` implements a standard tool-calling agent:

```
User message
    │
    ▼
Build system prompt (+ active skills + context + playbook summaries)
    │
    ▼
┌──► Send to LLM ──► Response
│        │
│        ├── Has tool calls? ──► Execute tools ──► Append results ──┐
│        │                                                          │
│        └── Final text? ──► Return to user                         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

The loop runs up to `maxIterations` times (default: 20). Each iteration may
include multiple tool calls executed in sequence. The agent supports two
virtual tools that do not call external services:

- **`select_skill`** -- loads a skill's markdown body into the system prompt
- **`set_context`** -- stores key-value pairs (like namespace or provider name)
  that persist for the session

## MCP integration

MCP servers expose tools over Streamable HTTP. The `MCPManager` connects to
each server defined in `mcp.json`, discovers available tools, and registers
them in the `ToolRegistry`.

When `kubeAuth` is `true` for a server entry, the agent automatically injects
`Authorization` (bearer token) and `X-Kubernetes-Server` (API URL) headers
into every MCP request. This is how the MCP containers access the OpenShift
cluster without needing their own kubeconfig.

## Skills and playbooks

**Skills** are markdown reference guides loaded on demand. When the LLM calls
the `select_skill` virtual tool, the skill body is injected into the system
prompt for subsequent turns.

**Playbooks** are task-oriented markdown files exposed in the web UI. When a
user selects a playbook, its body is sent as the initial user message, guiding
the agent through a multi-step workflow.

See [Skills and Playbooks](skills-and-playbooks.md) for details on authoring
custom content.

## Built-in tools

In addition to MCP tools, the agent registers these built-in tools:

| Tool | Description |
|---|---|
| `bash` | Execute shell commands (timeout configurable via `bashTimeout`) |
| `web_fetch` | Fetch a URL and convert to markdown (cached) |
| `select_skill` | Load a skill into the active system prompt |
| `set_context` | Set or unset session context key-value pairs |
