# mtv-agent

AI agent for [MTV/Forklift](https://github.com/kubev2v/forklift) VM migrations,
with a tool loop, MCP tool integration, and markdown-based skills and playbooks.

<div align="center">
  <img src="docs/mtv-agent-v0.1.0.png" alt="mtv-agent web UI" width="800" />
  <p><em>mtv-agent — chat interface with live migration metrics and plan status</em></p>
</div>

## Quick start

```bash
pip install mtv-agent
mtv-agent init
mtv-agent start             # with LM Studio (default)
mtv-agent start --with-cop  # with Claude
mtv-agent start --open      # open the web UI in your browser when ready
```

Or, using [uv](https://docs.astral.sh/uv/) (isolated install, no root needed):

```bash
uv tool install mtv-agent
```

Open `http://localhost:8000` in your browser, or use `mtv-agent start --open`. With `--no-web`, `--open` is ignored.

You need an OpenAI-compatible LLM backend, access to an OpenShift cluster with
MTV/Forklift, and Docker or Podman. See the
[Installation](docs/installation.md) and [Quick Start](docs/quickstart.md)
guides for the full walkthrough.

## Documentation

**User Guide**

- [Installation](docs/installation.md) -- prerequisites, install, and workspace setup
- [Quick Start](docs/quickstart.md) -- zero-to-running in under five minutes
- [LLM Backends](docs/llm-backends.md) -- LM Studio, Claude, and other OpenAI-compatible servers
- [Skills and Playbooks](docs/skills-and-playbooks.md) -- extending the agent with custom content

**Reference**

- [CLI Reference](docs/cli-reference.md) -- subcommands, flags, and credential resolution
- [Configuration](docs/configuration.md) -- `config.json`, `mcp.json`, and environment variables
- [API Reference](docs/api-reference.md) -- HTTP endpoints, SSE events, and examples
- [Architecture](docs/architecture.md) -- components, tool loop, and data flow

**Developer Guide**

- [Development](docs/development.md) -- contributor setup, dev workflows, and project structure
- [Publishing](docs/publishing.md) -- building and releasing to PyPI
- [Web UI](web/README.md) -- frontend architecture, components, and development

See [docs/index.md](docs/index.md) for the full documentation index.

## License

See [LICENSE](LICENSE).
