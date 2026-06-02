"""Configuration -- config.json (agent) + mcp.json (MCP servers)."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bundled data helpers
# ---------------------------------------------------------------------------

_PACKAGE_DIR = Path(__file__).resolve().parent
_PACKAGE_DATA = _PACKAGE_DIR / "data"

USER_DIR = Path.home() / ".mtv-agent"


def bundled_data_path(subpath: str) -> Path:
    """Resolve a path inside the bundled ``data/`` directory."""
    return _PACKAGE_DATA / subpath


def bundled_config_example() -> Path:
    return bundled_data_path("config.json.example")


def bundled_mcp_example() -> Path:
    return bundled_data_path("mcp.json.example")


# ---------------------------------------------------------------------------
# Config file discovery
# ---------------------------------------------------------------------------

_CONFIG_SEARCH_PATHS = [
    Path("config.json"),
    USER_DIR / "config.json",
]

_MCP_SEARCH_PATHS = [
    Path("mcp.json"),
    USER_DIR / "mcp.json",
]


def _find_file(name: str, override: str | None = None) -> Path | None:
    if override:
        p = Path(override).expanduser()
        return p if p.is_file() else None
    search = _MCP_SEARCH_PATHS if name == "mcp.json" else _CONFIG_SEARCH_PATHS
    for p in search:
        resolved = p.expanduser()
        if resolved.is_file():
            return resolved
    return None


def _load_json(name: str, override: str | None = None) -> dict:
    path = _find_file(name, override)
    if not path:
        search = _MCP_SEARCH_PATHS if name == "mcp.json" else _CONFIG_SEARCH_PATHS
        locations = "\n".join(f"  - {p.expanduser().resolve()}" for p in search)
        raise SystemExit(
            f"Error: {name} not found.\n\n"
            f"Searched:\n{locations}\n\n"
            f"Run 'mtv-agent init' to create a default configuration."
        )
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# MCP server config
# ---------------------------------------------------------------------------


@dataclass
class MCPServerConfig:
    """One MCP server entry from mcp.json."""

    name: str
    transport: str = "http"  # "http" or "stdio"
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    command: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] | None = None


def load_mcp_servers(override: str | None = None) -> list[MCPServerConfig]:
    """Parse mcp.json and return a list of server configs.

    If an explicit override path is given but doesn't exist, returns an empty
    list (useful for testing or running without external MCP servers).
    """
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            return []
        with open(path) as f:
            data = json.load(f)
    else:
        data = _load_json("mcp.json")

    servers: list[MCPServerConfig] = []
    for name, entry in data.get("mcpServers", {}).items():
        if not entry.get("enabled", True):
            continue
        servers.append(
            MCPServerConfig(
                name=name,
                transport=entry.get("transport", "http"),
                url=entry.get("url"),
                headers=entry.get("headers", {}),
                command=entry.get("command"),
                args=entry.get("args", []),
                env=entry.get("env"),
            )
        )
    return servers


# ---------------------------------------------------------------------------
# Application settings
# ---------------------------------------------------------------------------


_BUNDLED_SKILLS = str(_PACKAGE_DATA / "skills")
_BUNDLED_COMMANDS = str(_PACKAGE_DATA / "commands")


@dataclass
class Settings:
    """Flat application settings loaded from config.json + env."""

    llm_base_url: str = "http://localhost:1234/v1"
    llm_api_key: str = "not-needed"
    llm_model: str | None = None
    host: str = "0.0.0.0"
    port: int = 8000
    skills_dir: str = _BUNDLED_SKILLS
    commands_dir: str = _BUNDLED_COMMANDS
    cache_dir: str = "~/.mtv-agent/cache"
    max_iterations: int = 20
    mcp_config: str | None = None


def load_settings(override: str | None = None) -> Settings:
    """Load settings from config.json, falling back to defaults."""
    data = _load_json("config.json", override)
    llm = data.get("llm", {})
    srv = data.get("server", {})
    skills = data.get("skills", {})
    commands = data.get("commands", {})
    cache = data.get("cache", {})
    agent = data.get("agent", {})

    return Settings(
        llm_base_url=llm.get("baseUrl", Settings.llm_base_url),
        llm_api_key=llm.get("apiKey", Settings.llm_api_key),
        llm_model=llm.get("model"),
        host=os.environ.get("MTV_AGENT_HOST", srv.get("host", Settings.host)),
        port=int(os.environ.get("MTV_AGENT_PORT", srv.get("port", Settings.port))),
        skills_dir=skills.get("dir", Settings.skills_dir),
        commands_dir=commands.get("dir", Settings.commands_dir),
        cache_dir=cache.get("dir", Settings.cache_dir),
        max_iterations=agent.get("maxIterations", Settings.max_iterations),
    )


# ---------------------------------------------------------------------------
# TUI settings (read/write by the client side)
# ---------------------------------------------------------------------------

DEFAULT_THEME = "textual-dark"


def load_tui_theme() -> str:
    """Read the TUI theme from config.json (best-effort, returns default on error)."""
    path = _find_file("config.json")
    if not path:
        return DEFAULT_THEME
    try:
        data = json.loads(path.read_text())
        return data.get("tui", {}).get("theme", DEFAULT_THEME)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_THEME


def save_tui_theme(theme: str) -> None:
    """Persist the TUI theme into config.json."""
    path = _find_file("config.json")
    if not path:
        path = USER_DIR / "config.json"
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        data = {}
    data.setdefault("tui", {})["theme"] = theme
    path.write_text(json.dumps(data, indent=2) + "\n")
