"""Agent configuration -- unified config.json with env-var overrides."""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bundled data helpers
# ---------------------------------------------------------------------------

_PACKAGE_DIR = Path(__file__).resolve().parent


def _bundled_data_path(subpath: str) -> Path:
    """Resolve a path inside the bundled ``mtv_agent/data/`` directory."""
    return _PACKAGE_DIR / "data" / subpath


def bundled_config_example() -> Path:
    """Return the path to the bundled ``config.json.example``."""
    return _bundled_data_path("config.json.example")


_CONFIG_SEARCH_PATHS = [
    Path("config.json"),
    Path.home() / ".mtv-agent" / "config.json",
]


def _find_config_file() -> Path | None:
    """Return the first config file that exists on disk.

    Search order: ``CONFIG`` env var, then ``./config.json``,
    then ``~/.mtv-agent/config.json``.
    """
    env = os.environ.get("CONFIG")
    if env:
        p = Path(env).expanduser()
        return p if p.is_file() else None

    for p in _CONFIG_SEARCH_PATHS:
        resolved = p.expanduser()
        if resolved.is_file():
            return resolved
    return None


def _load_json_file(path: Path) -> dict[str, Any]:
    """Read and parse a JSON file, returning ``{}`` on any error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read config %s: %s", path, exc)
        return {}


def _flatten_config(data: dict[str, Any]) -> dict[str, Any]:
    """Map the nested camelCase JSON structure to flat snake_case fields."""
    flat: dict[str, Any] = {}

    llm = data.get("llm", {})
    if llm.get("baseUrl") is not None:
        flat["llm_base_url"] = llm["baseUrl"]
    if llm.get("apiKey") is not None:
        flat["llm_api_key"] = llm["apiKey"]
    if "model" in llm:
        flat["llm_model"] = llm["model"]

    server = data.get("server", {})
    if server.get("host") is not None:
        flat["server_host"] = server["host"]
    if server.get("port") is not None:
        flat["server_port"] = server["port"]

    skills = data.get("skills", {})
    if skills.get("dir") is not None:
        flat["skills_dir"] = skills["dir"]
    if skills.get("maxActive") is not None:
        flat["max_active_skills"] = skills["maxActive"]

    playbooks = data.get("playbooks", {})
    if playbooks.get("dir") is not None:
        flat["playbooks_dir"] = playbooks["dir"]

    mem = data.get("memory", {})
    if mem.get("maxTurns") is not None:
        flat["memory_max_turns"] = mem["maxTurns"]
    if mem.get("ttlSeconds") is not None:
        flat["memory_ttl_seconds"] = mem["ttlSeconds"]
    if mem.get("toolResultLimit") is not None:
        flat["memory_tool_result_limit"] = mem["toolResultLimit"]

    ag = data.get("agent", {})
    if ag.get("contextWindow") is not None:
        flat["context_window"] = ag["contextWindow"]
    if ag.get("maxIterations") is not None:
        flat["max_iterations"] = ag["maxIterations"]
    if ag.get("maxRetries") is not None:
        flat["max_retries"] = ag["maxRetries"]
    if ag.get("retryDelay") is not None:
        flat["retry_delay"] = ag["retryDelay"]

    cache = data.get("cache", {})
    if cache.get("dir") is not None:
        flat["cache_dir"] = cache["dir"]

    return flat


# ---------------------------------------------------------------------------
# MCP server config
# ---------------------------------------------------------------------------


@dataclass
class MCPServerConfig:
    """Connection details for a single MCP SSE server."""

    url: str
    headers: dict[str, str] = field(default_factory=dict)


def load_mcp_servers(data: dict[str, Any]) -> dict[str, MCPServerConfig]:
    """Extract MCP SSE server entries from a parsed config dict.

    Reads the top-level ``mcpServers`` key.  Entries that use ``command``
    (stdio transport) are skipped with a warning.
    """
    servers: dict[str, MCPServerConfig] = {}
    for name, entry in data.get("mcpServers", {}).items():
        if not isinstance(entry, dict):
            continue
        url = entry.get("url")
        if not url:
            if entry.get("command"):
                logger.warning(
                    "MCP server %r uses stdio transport (command) which is not "
                    "supported -- skipping",
                    name,
                )
            else:
                logger.warning("MCP server %r has no 'url' -- skipping", name)
            continue
        servers[name] = MCPServerConfig(
            url=url,
            headers=entry.get("headers", {}),
        )
    return servers


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

_config_path = _find_config_file()
_raw_config: dict[str, Any] = _load_json_file(_config_path) if _config_path else {}
_json_values = _flatten_config(_raw_config)


def _default_skills_dir() -> Path:
    """User dir if it exists, otherwise bundled data."""
    user = Path.home() / ".mtv-agent" / "skills"
    if user.is_dir():
        return user
    return _bundled_data_path("skills")


def _default_playbooks_dir() -> Path:
    """Local ``playbooks/`` if it exists, otherwise bundled data."""
    local = Path("playbooks")
    if local.is_dir():
        return local
    return _bundled_data_path("playbooks")


class Settings(BaseSettings):
    llm_base_url: str = "http://localhost:1234/v1"
    llm_api_key: str = "lm-studio"
    llm_model: str | None = None

    server_host: str = "0.0.0.0"
    server_port: int = 8000

    skills_dir: Path = _default_skills_dir()
    playbooks_dir: Path = _default_playbooks_dir()

    context_window: int = 30000
    max_active_skills: int = 3

    memory_max_turns: int = 20
    memory_ttl_seconds: int = 3600
    memory_tool_result_limit: int = 4000

    max_iterations: int = 20
    max_retries: int = 2
    retry_delay: float = 2.0

    cache_dir: Path = Path.home() / ".cache" / "mtv-agent"

    _json_values: ClassVar[dict[str, Any]] = _json_values

    model_config = {"env_prefix": ""}

    def model_post_init(self, __context: Any) -> None:
        """Apply JSON config values for fields not already set by env vars."""
        for key, value in self._json_values.items():
            env_name = key.upper()
            if env_name not in os.environ:
                if key in ("skills_dir", "playbooks_dir", "cache_dir"):
                    value = Path(value)
                setattr(self, key, value)


settings = Settings()

config_path: Path | None = _config_path
raw_config: dict[str, Any] = _raw_config
