"""Agent configuration -- split config.json (agent) + mcp.json (MCP servers)."""

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
    """Return the path to ``config.json.example``.

    Checks the bundled data dir first (pip-installed package), then
    falls back to the repo root (development from source).
    """
    bundled = _bundled_data_path("config.json.example")
    if bundled.is_file():
        return bundled
    repo_root = _PACKAGE_DIR.parent / "config.json.example"
    if repo_root.is_file():
        return repo_root
    return bundled


def bundled_mcp_example() -> Path:
    """Return the path to ``mcp.json.example``.

    Checks the bundled data dir first (pip-installed package), then
    falls back to the repo root (development from source).
    """
    bundled = _bundled_data_path("mcp.json.example")
    if bundled.is_file():
        return bundled
    repo_root = _PACKAGE_DIR.parent / "mcp.json.example"
    if repo_root.is_file():
        return repo_root
    return bundled


# ---------------------------------------------------------------------------
# Config file discovery
# ---------------------------------------------------------------------------

_config_path_override: str | None = None
_mcp_config_path_override: str | None = None

_CONFIG_SEARCH_PATHS = [
    Path("config.json"),
    Path.home() / ".mtv-agent" / "config.json",
]

_MCP_SEARCH_PATHS = [
    Path("mcp.json"),
    Path.home() / ".mtv-agent" / "mcp.json",
]


def _find_config_file() -> Path | None:
    """Return the first agent config file that exists on disk.

    Search order: explicit override, then ``./config.json``,
    then ``~/.mtv-agent/config.json``.
    """
    if _config_path_override:
        p = Path(_config_path_override).expanduser()
        return p if p.is_file() else None

    for p in _CONFIG_SEARCH_PATHS:
        resolved = p.expanduser()
        if resolved.is_file():
            return resolved
    return None


def _find_mcp_config_file() -> Path | None:
    """Return the first MCP config file that exists on disk.

    Search order: explicit override, then ``./mcp.json``,
    then ``~/.mtv-agent/mcp.json``.
    """
    if _mcp_config_path_override:
        p = Path(_mcp_config_path_override).expanduser()
        return p if p.is_file() else None

    for p in _MCP_SEARCH_PATHS:
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
    if ag.get("llmTimeout") is not None:
        flat["llm_timeout"] = ag["llmTimeout"]
    if ag.get("mcpToolTimeout") is not None:
        flat["mcp_tool_timeout"] = ag["mcpToolTimeout"]
    if ag.get("bashTimeout") is not None:
        flat["bash_timeout"] = ag["bashTimeout"]

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


def build_kube_auth_headers(api_url: str, token: str) -> dict[str, str]:
    """Build HTTP headers for MCP SSE auth from Kubernetes credentials.

    Returns an empty dict when both values are blank.
    """
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_url:
        headers["X-Kubernetes-Server"] = api_url
    return headers


def inject_kube_headers(
    servers: dict[str, "MCPServerConfig"],
    api_url: str,
    token: str,
) -> None:
    """Merge auto-resolved kube auth headers into every MCP server config.

    Headers already present in a server's config (e.g. set explicitly in
    ``mcp.json``) are **not** overwritten.
    """
    auto_headers = build_kube_auth_headers(api_url, token)
    if not auto_headers:
        return
    for cfg in servers.values():
        for key, value in auto_headers.items():
            cfg.headers.setdefault(key, value)


def load_mcp_servers(data: dict[str, Any]) -> dict[str, MCPServerConfig]:
    """Extract MCP SSE server entries from a parsed MCP config dict.

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


def _default_skills_dir() -> Path:
    """User dir if it exists, otherwise bundled data."""
    user = Path.home() / ".mtv-agent" / "skills"
    if user.is_dir():
        return user
    return _bundled_data_path("skills")


def _default_playbooks_dir() -> Path:
    """User dir if it exists, otherwise bundled data."""
    user = Path.home() / ".mtv-agent" / "playbooks"
    if user.is_dir():
        return user
    return _bundled_data_path("playbooks")


def _build_settings(json_values: dict[str, Any]) -> "Settings":
    """Create a Settings instance with the given JSON overrides."""

    class _S(BaseSettings):
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

        llm_timeout: int = 360
        mcp_tool_timeout: int = 360
        bash_timeout: int = 360

        cache_dir: Path = Path.home() / ".mtv-agent" / "cache"

        _json_values: ClassVar[dict[str, Any]] = json_values

        model_config = {"env_prefix": ""}

        def model_post_init(self, __context: Any) -> None:
            """Apply JSON config values for fields not already set by env vars."""
            try:
                for key, value in self._json_values.items():
                    env_name = key.upper()
                    if env_name not in os.environ:
                        if key in ("skills_dir", "playbooks_dir", "cache_dir"):
                            value = Path(value).expanduser()
                        setattr(self, key, value)
            except Exception as exc:
                raise RuntimeError(
                    "Failed initializing Settings from JSON overrides"
                ) from exc

    return _S()


# Keep Settings as a top-level name for type annotations elsewhere.
Settings = type(_build_settings({}))

# ---------------------------------------------------------------------------
# Module-level state (initial load)
# ---------------------------------------------------------------------------

_config_path = _find_config_file()
_raw_config: dict[str, Any] = _load_json_file(_config_path) if _config_path else {}

_mcp_config_path = _find_mcp_config_file()
_mcp_raw_config: dict[str, Any] = (
    _load_json_file(_mcp_config_path) if _mcp_config_path else {}
)

settings: Settings = _build_settings(_flatten_config(_raw_config))

config_path: Path | None = _config_path
raw_config: dict[str, Any] = _raw_config

mcp_config_path: Path | None = _mcp_config_path
mcp_raw_config: dict[str, Any] = _mcp_raw_config

# Runtime flag set by the orchestrator before uvicorn imports main.py.
no_web: bool = False


# ---------------------------------------------------------------------------
# Reload (called by the orchestrator when --config / --mcp-config is given)
# ---------------------------------------------------------------------------


def reload(
    config_path_arg: str | None = None,
    mcp_config_path_arg: str | None = None,
) -> None:
    """Re-discover and reload config files, updating module-level state.

    Call this *before* ``uvicorn.run()`` so that when ``main.py`` is
    imported it sees the freshly loaded values.
    """
    global _config_path_override, _mcp_config_path_override
    global settings, config_path, raw_config
    global mcp_config_path, mcp_raw_config

    if config_path_arg:
        _config_path_override = config_path_arg
    if mcp_config_path_arg:
        _mcp_config_path_override = mcp_config_path_arg

    # Agent config
    found = _find_config_file()
    raw = _load_json_file(found) if found else {}
    settings = _build_settings(_flatten_config(raw))
    config_path = found
    raw_config = raw

    # MCP config
    mcp_found = _find_mcp_config_file()
    mcp_raw = _load_json_file(mcp_found) if mcp_found else {}
    mcp_config_path = mcp_found
    mcp_raw_config = mcp_raw
