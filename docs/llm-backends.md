# LLM Backends

mtv-agent works with any OpenAI-compatible chat completion API. This document
covers the two tested options -- LM Studio and Claude -- as well as how to
connect any other compatible server.

> If you haven't installed mtv-agent yet, start with
> [Installation](installation.md).

## Option 1: LM Studio (local models)

[LM Studio](https://lmstudio.ai) lets you download and run open-weight LLMs
locally. It exposes an OpenAI-compatible API that mtv-agent can use directly.

### Setup

1. Download and install LM Studio from <https://lmstudio.ai>.
2. Open LM Studio, go to the **Discover** tab, and download a model. Good
   choices for tool-calling agents:
   - `Qwen2.5-Coder-32B-Instruct` (recommended -- strong tool use, 32B)
   - `Mistral-Small-24B-Instruct-2501` (fast, good tool support)
   - `Llama-3.1-8B-Instruct` (lightweight, decent for testing)
3. Go to the **Developer** tab and click **Start Server**. The default
   endpoint is `http://localhost:1234/v1`.

### Configuration

LM Studio on port 1234 is the default. After `mtv-agent init`, no configuration
changes are needed:

```bash
mtv-agent start
```

The agent auto-discovers the loaded model from `/v1/models` and detects the
context window from LM Studio's native API.

To override explicitly:

```bash
LLM_BASE_URL=http://localhost:1234/v1 LLM_MODEL=qwen2.5-coder-32b-instruct mtv-agent start
```

Or in `~/.mtv-agent/config.json`:

```json
{
  "llm": {
    "baseUrl": "http://localhost:1234/v1",
    "apiKey": "lm-studio",
    "model": "qwen2.5-coder-32b-instruct"
  }
}
```

### Tips

- **Context window**: LM Studio reports the model's context length
  automatically. The agent uses this to manage conversation history. If
  auto-detection fails, set `CONTEXT_WINDOW` (default: 30000).
- **GPU memory**: Larger models need more VRAM. 32B models typically require
  24 GB+. Use quantised variants (Q4, Q5) for lower memory usage.
- **Multiple models**: LM Studio can load multiple models. Use the
  `PUT /api/model` endpoint or the web UI's model selector to switch between
  them at runtime.

## Option 2: Claude via claude-openai-proxy

[claude-openai-proxy](https://github.com/yaacov/claude-openai-proxy) wraps the
`claude` CLI as an OpenAI-compatible server. This lets mtv-agent use Anthropic
Claude (Sonnet, Opus, etc.) without any code changes.

### Prerequisites

1. Install the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
   and authenticate:

   ```bash
   claude   # follow the login prompt
   ```

2. Verify it works:

   ```bash
   claude -p "hello"
   ```

### How it works

`claude-openai-proxy` is a lightweight Python server that:

- Listens on port 1234 (configurable via `PORT`)
- Accepts standard OpenAI `/v1/chat/completions` requests
- Translates them into `claude` CLI invocations
- Returns the response in OpenAI format, including tool calls

Since it is listed as a dependency of `mtv-agent`, it is installed
automatically with `pip install mtv-agent`. No separate installation step is
needed.

### Usage with mtv-agent start

The simplest way is to pass `--with-cop`, which starts the proxy automatically:

```bash
mtv-agent start --with-cop
```

This starts `claude-openai-proxy` on port 1234 in the background, then boots
the agent configured to use it. On shutdown (`Ctrl-C`), the proxy is stopped
along with the MCP containers.

### Running the proxy manually

If you prefer to manage the proxy yourself:

```bash
# Terminal 1: start the proxy
PORT=1234 claude-openai-proxy

# Terminal 2: start the agent
mtv-agent serve
```

Or with a custom port:

```bash
# Terminal 1
PORT=5000 claude-openai-proxy

# Terminal 2
LLM_BASE_URL=http://localhost:5000/v1 mtv-agent serve
```

### Configuration

When using `--with-cop`, the default `~/.mtv-agent/config.json` (created by
`mtv-agent init`) points at `http://localhost:1234/v1`, which is the proxy's
address. No extra configuration is required.

To use Claude alongside a custom config:

```json
{
  "llm": {
    "baseUrl": "http://localhost:1234/v1",
    "apiKey": "not-needed",
    "model": null
  }
}
```

The `apiKey` value is ignored by the proxy (authentication is handled by the
`claude` CLI's stored credentials). The `model` field can be left `null` for
auto-discovery, or set to a specific model name reported by the proxy.

### Tips

- **Authentication**: The proxy uses whatever credentials the `claude` CLI is
  configured with. Make sure `claude -p "test"` works before starting the proxy.
- **Rate limits**: Claude API rate limits apply. For heavy usage, consider a
  Claude Pro or Team plan.
- **Streaming**: The proxy supports streaming responses, which the agent uses
  for real-time token output in the web UI.

## Option 3: Other OpenAI-compatible servers

Any server that implements the OpenAI `/v1/chat/completions` and `/v1/models`
endpoints can be used. Examples include:

- [Ollama](https://ollama.com) -- `LLM_BASE_URL=http://localhost:11434/v1`
- [vLLM](https://docs.vllm.ai) -- `LLM_BASE_URL=http://localhost:8000/v1`
- [OpenAI API](https://platform.openai.com) -- set `LLM_BASE_URL=https://api.openai.com/v1` and `LLM_API_KEY` to your API key
- [Together AI](https://together.ai), [Groq](https://groq.com), and similar hosted providers

Set `LLM_BASE_URL` and `LLM_API_KEY` in your environment or in
`config.json`. The agent will auto-discover the model name unless you set
`LLM_MODEL` explicitly.

> **Tool calling support is required.** The agent relies on the LLM returning
> structured tool calls. Models or providers that do not support tool calling
> will not work correctly.

## Switching between backends

You can switch backends at any time:

- **At startup**: use `--with-cop` for Claude, or omit it for LM Studio.
- **At runtime**: use the `PUT /api/model` endpoint or the model selector in
  the web UI. Note that switching between backends requires changing
  `LLM_BASE_URL`, which means restarting the agent.
- **Via environment**: set `LLM_BASE_URL` to point at whichever server you want.

## Comparison

| Feature | LM Studio | Claude (via proxy) |
|---|---|---|
| Cost | Free (runs locally) | API usage fees |
| Speed | Depends on hardware | Fast (API-based) |
| Privacy | Fully local | Data sent to Anthropic |
| Model quality | Varies by model | State-of-the-art |
| GPU required | Yes (recommended) | No |
| Tool calling | Model-dependent | Excellent |
| Setup | Download app + model | Install CLI + authenticate |
