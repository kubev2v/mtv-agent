"""Tests for mtv_agent.server.config."""

import json
import tempfile

import pytest

from mtv_agent.server.config import Settings, load_mcp_servers, load_settings


def test_default_settings():
    s = Settings()
    assert s.llm_base_url == "http://localhost:1234/v1"
    assert s.port == 8000
    assert s.max_iterations == 20


def test_load_settings_from_file():
    data = {
        "llm": {"baseUrl": "http://myhost:9999/v1", "model": "gpt-test"},
        "server": {"port": 3000},
        "agent": {"maxIterations": 5},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        s = load_settings(f.name)
    assert s.llm_base_url == "http://myhost:9999/v1"
    assert s.llm_model == "gpt-test"
    assert s.port == 3000
    assert s.max_iterations == 5


def test_load_settings_missing_file():
    with pytest.raises(SystemExit, match="config.json not found"):
        load_settings("/nonexistent/path.json")


def test_load_mcp_servers_from_file():
    data = {
        "mcpServers": {
            "test-http": {"transport": "http", "url": "http://localhost:9090/mcp"},
            "test-stdio": {
                "transport": "stdio",
                "command": "my-cmd",
                "args": ["--flag"],
            },
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        servers = load_mcp_servers(f.name)
    assert len(servers) == 2
    http_srv = next(s for s in servers if s.name == "test-http")
    assert http_srv.transport == "http"
    assert http_srv.url == "http://localhost:9090/mcp"
    stdio_srv = next(s for s in servers if s.name == "test-stdio")
    assert stdio_srv.transport == "stdio"
    assert stdio_srv.command == "my-cmd"
    assert stdio_srv.args == ["--flag"]


def test_load_mcp_servers_missing_file():
    result = load_mcp_servers("/nonexistent/mcp.json")
    assert result == []
