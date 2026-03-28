# API Reference

All endpoints are served under the `/api` prefix. The default base URL is
`http://localhost:8000/api`.

## Chat

### `POST /api/chat`

Non-streaming chat. Sends a message and returns the complete answer as JSON.

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | yes | The user message |
| `session_id` | string | no | Session ID for conversation history (auto-generated if omitted) |
| `skills` | string[] | no | Skill names to activate for this request |
| `context` | object | no | Key-value context pairs (e.g. `{"namespace": "default"}`) |

### `POST /api/chat/stream`

Streaming chat. Emits Server-Sent Events (SSE) as the agent works.

```bash
curl -N http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "list migration plans"}'
```

Add `?approve=true` to require manual approval before each tool execution.

**Request body:** Same as `POST /api/chat`.

**SSE event types:**

| Event | Payload | Description |
|---|---|---|
| `session` | `{"session_id": "..."}` | Session ID for this conversation |
| `thinking` | | Agent is waiting for the LLM |
| `usage` | `{"total_tokens", "prompt_tokens", "completion_tokens", "context_window"}` | Token usage for the current turn |
| `tool_call` | `{"name", "arguments"}` | Tool about to be executed |
| `tool_result` | `{"name", "result"}` | Tool execution result |
| `tool_denied` | `{"name", "reason"}` | Tool denied by user (approval mode) |
| `skill_selected` | `{"name"}` | Skill activated by the agent |
| `skill_cleared` | | All skills deactivated |
| `context_set` | `{"key", "value"}` | Context key updated |
| `context_unset` | `{"key"}` | Context key removed |
| `content` | text | Final assistant response text |
| `done` | `{"content"}` | Stream complete; includes the final response |

### `POST /api/chat/{session_id}/approve`

Push an approval decision for a pending tool call (used with `?approve=true`).

**Approve:**

```json
{"approved": true}
```

**Deny (with optional reason):**

```json
{"approved": false, "reason": "too dangerous"}
```

### `POST /api/chat/{session_id}/cancel`

Cancel a running agent loop for the given session.

## Chat history

### `GET /api/chats`

List all saved chats, newest first. Each entry includes `id`, `title`, and
`updated_at`.

### `GET /api/chats/{chat_id}`

Load a saved chat with full message history.

### `DELETE /api/chats/{chat_id}`

Delete a saved chat.

### `PUT /api/chats/{chat_id}/title`

Rename a saved chat.

```json
{"title": "new name"}
```

## Tools

### `GET /api/tools`

List available tools with `name`, short `description`, and `parameters` JSON
schema.

### `POST /api/tools/{tool_name}`

Execute a registered tool directly, bypassing the LLM agent loop.

```json
{"arguments": {"command": "get plan"}}
```

## Status and models

### `GET /api/status`

Returns the current model name, connected MCP servers, tool count, context
window size, and max active skills.

### `GET /api/models`

List models available on the configured LLM server.

### `PUT /api/model`

Hot-swap the active model at runtime.

```json
{"model": "model-name"}
```

## Skills and playbooks

### `GET /api/skills`

List available skills with names and descriptions.

### `GET /api/playbooks`

List available playbooks with metadata and body content.

## MCP servers

### `GET /api/mcp`

List all configured MCP servers with their connection status.

### `POST /api/mcp/{name}`

Connect an MCP server by name.

### `DELETE /api/mcp/{name}`

Disconnect an MCP server by name.
