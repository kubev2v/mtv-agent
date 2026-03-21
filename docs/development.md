# Development

This guide is for contributors working from a git checkout of the
[mtv-agent](https://github.com/yaacov/mtv-agent) repository.

## Setup from source

```bash
git clone https://github.com/yaacov/mtv-agent.git
cd mtv-agent
uv sync --extra dev
```

This creates a `.venv/`, installs all dependencies, and sets up the package
in editable mode. Use `uv run` to execute commands inside the venv without
activating it manually:

```bash
uv run mtv-agent --version
```

For the web UI you also need Node.js (v18+):

```bash
cd web && npm ci && cd ..
```

## Running in dev mode

If you've logged in with `oc login` or configured `kubectl`, the dev scripts
read credentials from your kubeconfig automatically. Otherwise, set them
explicitly:

```bash
export KUBE_API_URL=https://api.cluster.example.com:6443
export KUBE_TOKEN=$(oc whoami -t)
```

Then use the Make targets:

```bash
make run        # MCP containers + API server (uses local LLM)
make run-cop    # same, but also starts claude-openai-proxy
make build-web  # build the web UI into web/dist/ (served automatically)
make stop       # stop MCP containers and claude-openai-proxy
```

The API server auto-detects `web/dist/` and serves it at
`http://localhost:8000`. If you haven't built the web UI yet, the API
still works -- you just won't see the browser interface.

## Frontend development

For frontend work you want the Vite dev server (with hot-module reload)
alongside the API server. Run them in two terminals:

```bash
# Terminal 1 -- API server without static file serving
make dev

# Terminal 2 -- Vite dev server on port 5173
make dev-web
```

`make dev` passes `--no-web` so the API server does not serve static files,
avoiding conflicts with Vite. The Vite dev server proxies `/api` requests
to the API server on port 8000 automatically.

## Make targets reference

| Target | Description |
|---|---|
| `make run` | Start MCP containers + API server via `mtv-agent start` |
| `make run-cop` | Same as `run` but also starts claude-openai-proxy |
| `make dev` | Start MCP containers + API server with `--no-web` (for frontend dev) |
| `make serve` | Start only the API server (no containers) |
| `make build-web` | Build the web UI into `web/dist/` |
| `make dev-web` | Start the Vite dev server for the web UI |
| `make stop` | Stop MCP containers and claude-openai-proxy |
| `make format` | Auto-format Python code with ruff |
| `make format-web` | Auto-format web code with prettier |
| `make lint` | Lint Python code with ruff |
| `make lint-web` | Lint web code with eslint + prettier |
| `make package` | Build the pip-distributable wheel (includes web UI) |
| `make help` | Show all targets |

## Linting and formatting

```bash
make lint       # ruff check + format check
make format     # ruff auto-fix + format

make lint-web   # eslint + prettier check
make format-web # prettier auto-fix
```

## Building the pip package

```bash
make package
```

This runs `make build-web` first, copies `web/dist/` into `mtv_agent/web_dist/`,
then runs `python -m build` to produce a distributable wheel in `dist/`.

## Project structure

```
mtv-agent/
├── mtv_agent/               # Python package (pip-installable)
│   ├── __init__.py          # Version
│   ├── __main__.py          # python -m mtv_agent
│   ├── cli.py               # CLI entry point (mtv-agent command)
│   ├── orchestrator.py      # Container + process lifecycle management
│   ├── main.py              # FastAPI app, /api endpoints, static serving
│   ├── agent.py             # The tool loop (LLM -> tools -> results -> LLM)
│   ├── config.py            # Settings (config.json + mcp.json, env-var overrides)
│   ├── lib/                 # Internal libraries
│   │   ├── bash_tool.py     # Built-in bash tool for shell commands
│   │   ├── chat_store.py    # Persistent chat storage (JSON files)
│   │   ├── html_to_md.py    # HTML-to-markdown conversion
│   │   ├── kubeconfig.py    # Kubeconfig credential extraction (via k8s client)
│   │   ├── llm.py           # OpenAI-compatible LLM client
│   │   ├── mcp_client.py    # MCP SSE client
│   │   ├── mcp_manager.py   # Multi-MCP server manager
│   │   ├── md_sections.py   # Markdown section utilities
│   │   ├── memory.py        # In-memory conversation history
│   │   ├── playbooks.py     # Playbook markdown loader
│   │   ├── skills.py        # Skill markdown loader
│   │   ├── system_prompt.py # System prompt builder
│   │   ├── text_utils.py    # Truncation, frontmatter parsing
│   │   ├── tool_registry.py # Unified registry (bash + MCP tools)
│   │   ├── virtual_tools.py # select_skill, set_context tools
│   │   ├── web_cache.py     # Web content cache
│   │   └── web_tool.py      # Built-in web fetch tool
│   └── data/                # Bundled data (included in pip package)
│       ├── config.json.example
│       ├── mcp.json.example
│       ├── skills/
│       └── playbooks/
├── web/                     # Web UI source (Lit + TypeScript, not packaged)
│   ├── src/
│   ├── dist/                # Built assets (served by Python server)
│   └── package.json
├── docs/                    # Documentation
│   ├── installation.md      # Prerequisites, install, workspace setup
│   ├── quickstart.md        # Zero-to-running walkthrough
│   ├── llm-backends.md      # LM Studio and Claude setup guide
│   └── development.md       # This file
├── Makefile                 # Dev and build targets
└── pyproject.toml           # Package metadata and dependencies
```
