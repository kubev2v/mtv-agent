# mtv-agent Documentation

AI agent for [MTV/Forklift](https://github.com/kubev2v/forklift) VM migrations,
with a tool loop, MCP tool integration, and markdown-based skills and playbooks.

## User Guide

Step-by-step guides for installing, configuring, and using mtv-agent.

- [Installation](installation.md) -- prerequisites, install methods, and workspace setup
- [Quick Start](quickstart.md) -- go from a fresh install to a running agent in under five minutes
- [LLM Backends](llm-backends.md) -- set up LM Studio, Claude, or any OpenAI-compatible server
- [Skills and Playbooks](skills-and-playbooks.md) -- understand, use, and author custom skills and playbooks

## Reference

Fact-oriented lookup pages for CLI flags, configuration keys, and API endpoints.

- [CLI Reference](cli-reference.md) -- all subcommands, flags, and cluster credential resolution
- [Configuration](configuration.md) -- `config.json`, `mcp.json`, and environment variable overrides
- [API Reference](api-reference.md) -- HTTP endpoints, request/response bodies, and SSE event types
- [Architecture](architecture.md) -- component diagram, agent tool loop, and data flow

## Developer Guide

For contributors working from a git checkout of the repository.

- [Development](development.md) -- source setup, Make targets, linting, packaging, and project structure
- [Web UI](../web/README.md) -- frontend architecture, Lit components, themes, and API communication
- [MCP Metrics Issues](mcp-metrics-issues.md) -- known issues in the kubectl-metrics MCP server
