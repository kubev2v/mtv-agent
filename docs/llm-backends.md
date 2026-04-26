# LLM Backends

mtv-agent works with any OpenAI-compatible chat completion API. The backend
is selected by the `llm.type` field in `~/.mtv-agent/config.json`:

| `llm.type` | Description |
|---|---|
| `claude-vertex` | Claude on Google Cloud Vertex AI (default) |
| `openai` | Any OpenAI-compatible server (LM Studio, Ollama, vLLM, OpenAI API, etc.) |

> If you haven't installed mtv-agent yet, start with
> [Installation](installation.md).

## Option 1: Claude via Vertex AI (default)

The default configuration uses Claude on Google Cloud Vertex AI. A bundled
proxy ([claude-openai-proxy](https://github.com/yaacov/claude-openai-proxy))
translates OpenAI-compatible API calls into Anthropic Vertex AI calls. The
proxy is started automatically when `llm.type` is `"claude-vertex"`.

### Prerequisites

1. A Google Cloud project with the **Anthropic Vertex AI API** enabled.

2. Authenticate with Google Cloud:

   ```bash
   gcloud auth application-default login
   ```

3. Set the required environment variables:

   ```bash
   export CLOUD_ML_REGION=us-east5              # or your preferred region
   export ANTHROPIC_VERTEX_PROJECT_ID=my-project # your GCP project ID
   ```

### Configuration

After `mtv-agent init`, the default `~/.mtv-agent/config.json` is already
configured for Claude on Vertex AI:

```json
{
  "llm": {
    "type": "claude-vertex",
    "baseUrl": "http://localhost:1234/v1",
    "apiKey": "not-needed",
    "model": null
  }
}
```

When `llm.type` is `"claude-vertex"`, the `baseUrl` and `apiKey` fields are
ignored -- the agent starts the proxy automatically on port 1234 and
overrides the URL to point at it. The `model` field can be left `null` for
auto-discovery.

Start the agent:

```bash
CLOUD_ML_REGION=us-east5 ANTHROPIC_VERTEX_PROJECT_ID=my-project \
  mtv-agent start
```

### How it works

`claude-openai-proxy` is a lightweight Python server that:

- Listens on port 1234 (configurable via `MTV_AGENT_COP_PORT`)
- Accepts standard OpenAI `/v1/chat/completions` requests
- Translates them into Anthropic Vertex AI API calls
- Returns the response in OpenAI format, including tool calls

Since it is listed as a dependency of `mtv-agent`, it is installed
automatically with `pip install mtv-agent`. No separate installation step is
needed.

### Tips

- **Authentication**: The proxy uses Google Cloud Application Default
  Credentials. Make sure `gcloud auth application-default login` has been
  run and that `CLOUD_ML_REGION` and `ANTHROPIC_VERTEX_PROJECT_ID` are set.
- **Rate limits**: Vertex AI quota limits apply. Check your project's quotas
  in the Google Cloud console.
- **Streaming**: The proxy supports streaming responses, which the agent uses
  for real-time token output in the web UI.

## Option 2: LM Studio (local models)

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

Set `llm.type` to `"openai"` in `~/.mtv-agent/config.json`:

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

Then start the agent:

```bash
mtv-agent start
```

The agent auto-discovers the loaded model from `/v1/models` and detects the
context window from LM Studio's native API.

To override explicitly:

```bash
LLM_BASE_URL=http://localhost:1234/v1 LLM_MODEL=qwen2.5-coder-32b-instruct mtv-agent start
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

## Option 3: Other OpenAI-compatible servers

Any server that implements the OpenAI `/v1/chat/completions` and `/v1/models`
endpoints can be used. Set `llm.type` to `"openai"` and configure the URL.
Examples:

- [Ollama](https://ollama.com) -- `"baseUrl": "http://localhost:11434/v1"`
- [vLLM](https://docs.vllm.ai) -- `"baseUrl": "http://localhost:8000/v1"`
- [OpenAI API](https://platform.openai.com) -- `"baseUrl": "https://api.openai.com/v1"` and set `apiKey` to your API key
- [Together AI](https://together.ai), [Groq](https://groq.com), and similar hosted providers

Set `llm.type`, `llm.baseUrl`, and `llm.apiKey` in `config.json`, or use
environment variables (`LLM_TYPE`, `LLM_BASE_URL`, `LLM_API_KEY`). The agent
will auto-discover the model name unless you set `LLM_MODEL` explicitly.

> **Tool-calling support is required.** The agent relies on the LLM returning
> structured tool calls. Models or providers that do not support tool calling
> will not work correctly.

## Switching between backends

You can switch backends by changing `llm.type` in `~/.mtv-agent/config.json`:

- Set `"type": "claude-vertex"` for Claude on Vertex AI (proxy starts
  automatically).
- Set `"type": "openai"` for LM Studio or any other OpenAI-compatible server.

You can also override at startup with environment variables:

```bash
LLM_TYPE=openai LLM_BASE_URL=http://localhost:1234/v1 mtv-agent start
```

The legacy `--with-cop` flag still works and forces `claude-vertex` mode
for the current run, regardless of the config file setting.

## Comparison

| Feature | LM Studio | Claude (via Vertex AI proxy) |
|---|---|---|
| Cost | Free (runs locally) | Vertex AI usage fees |
| Speed | Depends on hardware | Fast (API-based) |
| Privacy | Fully local | Data sent to Google Cloud |
| Model quality | Varies by model | State-of-the-art |
| GPU required | Yes (recommended) | No |
| Tool calling | Model-dependent | Excellent |
| Setup | Download app + model | GCP project + gcloud auth |
