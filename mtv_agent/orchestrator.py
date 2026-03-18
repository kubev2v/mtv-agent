"""Orchestrate MCP containers, claude-openai-proxy, and the API server."""

from __future__ import annotations

import atexit
import json
import logging
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import uvicorn

from mtv_agent.config import _bundled_data_path, bundled_config_example, settings
from mtv_agent.lib.kubeconfig import resolve_kube_credentials, set_kube_credentials

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP container definitions
# ---------------------------------------------------------------------------

_DEFAULT_IMAGES = {
    "kubectl-mtv": "quay.io/yaacov/kubectl-mtv-mcp-server:latest",
    "kubectl-metrics": "quay.io/yaacov/kubectl-metrics-mcp-server:latest",
    "kubectl-debug-queries": "quay.io/yaacov/kubectl-debug-queries-mcp-server:latest",
}

_MCP_SERVERS = [
    {
        "name": "mtv-agent-mcp-mtv",
        "host_port": 8080,
        "config_key": "kubectl-mtv",
        "sse_path": "/sse",
    },
    {
        "name": "mtv-agent-mcp-metrics",
        "host_port": 8081,
        "config_key": "kubectl-metrics",
        "sse_path": "/sse",
    },
    {
        "name": "mtv-agent-mcp-debug-queries",
        "host_port": 8082,
        "config_key": "kubectl-debug-queries",
        "sse_path": "/sse",
    },
]

COP_PORT = 1234


@dataclass
class _RunState:
    """Tracks processes and containers started by the orchestrator."""

    runtime: str = ""
    container_names: list[str] = None  # type: ignore[assignment]
    cop_proc: subprocess.Popen | None = None

    def __post_init__(self) -> None:
        if self.container_names is None:
            self.container_names = []


_state = _RunState()


# ---------------------------------------------------------------------------
# Container runtime detection
# ---------------------------------------------------------------------------


def detect_runtime(preferred: str | None = None) -> str:
    """Return ``docker`` or ``podman``, preferring *preferred* if given."""
    if preferred:
        if shutil.which(preferred):
            return preferred
        raise RuntimeError(f"Requested runtime '{preferred}' not found in PATH")
    for candidate in ("docker", "podman"):
        if shutil.which(candidate):
            return candidate
    raise RuntimeError("Neither docker nor podman found in PATH")


# ---------------------------------------------------------------------------
# Readiness probe
# ---------------------------------------------------------------------------


def _wait_for_port(
    host: str,
    port: int,
    label: str,
    timeout: int = 60,
    interval: float = 1.0,
) -> bool:
    """Block until *host*:*port* accepts a TCP connection, or *timeout* expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("  %s is ready", label)
                return True
        except (ConnectionRefusedError, OSError):
            pass
        time.sleep(interval)
    logger.warning("  %s did not become ready within %ds", label, timeout)
    return False


# ---------------------------------------------------------------------------
# Container lifecycle
# ---------------------------------------------------------------------------


def _run_container(
    runtime: str,
    name: str,
    image: str,
    host_port: int,
) -> None:
    """Start a single MCP container in detached mode.

    Credentials are **not** baked into the container; the API server
    sends them as HTTP headers on each SSE connection instead.
    """
    subprocess.run(
        [runtime, "rm", "-f", name],
        capture_output=True,
    )
    cmd = [
        runtime,
        "run",
        "--rm",
        "-d",
        "--name",
        name,
        "-p",
        f"{host_port}:8080",
        "-e",
        "MCP_KUBE_INSECURE=true",
        image,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    logger.info("  %s -> http://localhost:%d/sse", name, host_port)


def _resolve_image(config_key: str, raw_config: dict | None) -> str | None:
    """Return the container image for *config_key*, or ``None`` to skip.

    Resolution order:
    1. ``mcpServers.<config_key>.image`` in the raw config (explicit).
       A ``null`` / empty value means "no container" -- the server is remote.
    2. If the config has no ``mcpServers`` section at all (or no entry for
       this key), fall back to the hardcoded default.
    """
    if raw_config:
        mcp_section = raw_config.get("mcpServers", {})
        entry = mcp_section.get(config_key, {})
        if isinstance(entry, dict) and "image" in entry:
            return entry["image"] or None
    return _DEFAULT_IMAGES[config_key]


def start_mcp_containers(
    runtime: str,
    raw_config: dict | None = None,
) -> list[str]:
    """Start MCP server containers, waiting for each to become ready.

    Containers are started **without** Kubernetes credentials; the API
    server passes them via HTTP headers on each SSE connection.

    Servers whose config entry has ``"image": null`` (or no image) are
    skipped -- they are assumed to be running remotely.
    """
    logger.info("Starting MCP servers (%s)...", runtime)
    names: list[str] = []
    for srv in _MCP_SERVERS:
        image = _resolve_image(srv["config_key"], raw_config)
        if not image:
            logger.info(
                "  %s -- no image configured, skipping (remote)",
                srv["config_key"],
            )
            continue
        _run_container(
            runtime,
            srv["name"],
            image,
            srv["host_port"],
        )
        _wait_for_port("localhost", srv["host_port"], srv["name"])
        names.append(srv["name"])
    return names


def stop_containers(runtime: str, names: list[str]) -> None:
    """Stop and remove the given containers."""
    for name in names:
        subprocess.run(
            [runtime, "stop", name],
            capture_output=True,
        )


def stop_mcp_containers_any_runtime() -> None:
    """Best-effort stop of MCP containers using any available runtime."""
    for candidate in ("docker", "podman"):
        if not shutil.which(candidate):
            continue
        for srv in _MCP_SERVERS:
            subprocess.run(
                [candidate, "stop", srv["name"]],
                capture_output=True,
            )


# ---------------------------------------------------------------------------
# Claude OpenAI Proxy
# ---------------------------------------------------------------------------


def start_cop(port: int = COP_PORT) -> subprocess.Popen:
    """Start claude-openai-proxy as a background subprocess."""
    logger.info("Starting claude-openai-proxy on port %d...", port)
    env = {**os.environ, "PORT": str(port)}
    proc = subprocess.Popen(
        [sys.executable, "-m", "claude_openai_proxy"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    logger.info("  claude-openai-proxy -> http://localhost:%d", port)
    return proc


def stop_cop(proc: subprocess.Popen | None) -> None:
    """Terminate the COP subprocess if running."""
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def stop_cop_by_name() -> None:
    """Best-effort kill of any running claude-openai-proxy process."""
    subprocess.run(
        ["pkill", "-f", "claude_openai_proxy"],
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# Config generation
# ---------------------------------------------------------------------------


def _load_config_file(path: str) -> dict:
    """Read and parse a config JSON file, returning ``{}`` on any error."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def generate_config(config_path: str | None = None) -> str:
    """Ensure a config file exists. Returns the path used.

    If *config_path* is given and exists, it is returned as-is.
    Otherwise the standard search paths are checked.  When no config
    file is found anywhere, a default is created at
    ``~/.mtv-agent/config.json``.
    """
    if config_path:
        p = Path(config_path).expanduser()
        if p.is_file():
            return str(p)

    for candidate in (Path("config.json"), Path.home() / ".mtv-agent" / "config.json"):
        if candidate.expanduser().is_file():
            return str(candidate.expanduser())

    example = bundled_config_example()
    if example.is_file():
        data = json.loads(example.read_text(encoding="utf-8"))
    else:
        data = _default_config_dict()

    persistent = Path.home() / ".mtv-agent" / "config.json"
    persistent.parent.mkdir(parents=True, exist_ok=True)
    persistent.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    logger.info("Created default config: %s", persistent)
    return str(persistent)


def get_default_config_text() -> str:
    """Return the default config JSON as a formatted string."""
    example = bundled_config_example()
    if example.is_file():
        return example.read_text(encoding="utf-8")
    return json.dumps(_default_config_dict(), indent=2) + "\n"


def _default_config_dict() -> dict:
    return {
        "llm": {
            "baseUrl": "http://localhost:1234/v1",
            "apiKey": "lm-studio",
            "model": None,
        },
        "server": {"host": "0.0.0.0", "port": 8000},
        "mcpServers": {
            "kubectl-mtv": {
                "url": "http://localhost:8080/sse",
                "image": "quay.io/yaacov/kubectl-mtv-mcp-server:latest",
            },
            "kubectl-metrics": {
                "url": "http://localhost:8081/sse",
                "image": "quay.io/yaacov/kubectl-metrics-mcp-server:latest",
            },
            "kubectl-debug-queries": {
                "url": "http://localhost:8082/sse",
                "image": "quay.io/yaacov/kubectl-debug-queries-mcp-server:latest",
            },
        },
        "skills": {"dir": "~/.mtv-agent/skills", "maxActive": 3},
        "playbooks": {"dir": "~/.mtv-agent/playbooks"},
        "memory": {"maxTurns": 20, "ttlSeconds": 3600, "toolResultLimit": 4000},
        "agent": {
            "contextWindow": 30000,
            "maxIterations": 20,
            "maxRetries": 2,
            "retryDelay": 2.0,
        },
        "cache": {"dir": "~/.mtv-agent/cache"},
    }


# ---------------------------------------------------------------------------
# Workspace initialisation
# ---------------------------------------------------------------------------

_INIT_DIR = Path.home() / ".mtv-agent"


def init_workspace(target: Path | None = None, *, force: bool = False) -> Path:
    """Copy bundled config, skills, and playbooks into a local workspace.

    Returns the directory that was initialised.  Files that already exist
    are skipped unless *force* is ``True``.
    """
    dest = (target or _INIT_DIR).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []

    # Config is user-editable -- only overwrite with --force.
    config_src = bundled_config_example()
    config_dst = dest / "config.json"
    if config_dst.exists() and not force:
        skipped.append("config.json")
    else:
        shutil.copy2(config_src, config_dst)
        created.append("config.json")

    # Skills and playbooks are bundled defaults -- always refresh so
    # users get updates on new versions without needing --force.
    skills_src = _bundled_data_path("skills")
    skills_dst = dest / "skills"
    if skills_dst.exists():
        shutil.rmtree(skills_dst)
    shutil.copytree(skills_src, skills_dst)
    created.append("skills/")

    playbooks_src = _bundled_data_path("playbooks")
    playbooks_dst = dest / "playbooks"
    if playbooks_dst.exists():
        shutil.rmtree(playbooks_dst)
    shutil.copytree(playbooks_src, playbooks_dst)
    created.append("playbooks/")

    logger.info("Initialised workspace: %s", dest)
    if created:
        logger.info("  created/updated: %s", ", ".join(created))
    if skipped:
        logger.info("  skipped (already exist): %s", ", ".join(skipped))

    return dest


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------


def _cleanup() -> None:
    """Shut down all managed processes and containers."""
    logger.info("Shutting down...")
    stop_cop(_state.cop_proc)
    _state.cop_proc = None
    if _state.runtime and _state.container_names:
        stop_containers(_state.runtime, _state.container_names)
        _state.container_names.clear()
    logger.info("Done.")


def _signal_handler(signum: int, frame) -> None:
    _cleanup()
    sys.exit(0)


# ---------------------------------------------------------------------------
# Full-stack launch
# ---------------------------------------------------------------------------


def start_all(
    *,
    with_cop: bool = False,
    config_path: str | None = None,
    runtime: str | None = None,
    host: str | None = None,
    port: int | None = None,
    no_web: bool = False,
    kube_api_url: str | None = None,
    kube_token: str | None = None,
    kubeconfig: str | None = None,
    kube_context: str | None = None,
) -> None:
    """Start MCP containers, optionally COP, then the API server (blocking)."""
    api_url, token = resolve_kube_credentials(
        kube_api_url, kube_token, kubeconfig, kube_context
    )
    if not api_url:
        print(
            "Error: Kubernetes API URL not found.\n"
            "  Pass --kube-api-url, set KUBE_API_URL, or configure a kubeconfig.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not token:
        print(
            "Error: Kubernetes token not found.\n"
            "  Pass --kube-token, set KUBE_TOKEN, or configure a kubeconfig.",
            file=sys.stderr,
        )
        sys.exit(1)

    rt = detect_runtime(runtime)
    _state.runtime = rt

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    atexit.register(_cleanup)

    cfg = generate_config(config_path)
    os.environ["CONFIG"] = cfg

    if with_cop:
        _state.cop_proc = start_cop()
        _wait_for_port("localhost", COP_PORT, "claude-openai-proxy")

    raw_cfg = _load_config_file(cfg)
    _state.container_names = start_mcp_containers(rt, raw_config=raw_cfg)

    serve(host=host, port=port, no_web=no_web, kube_api_url=api_url, kube_token=token)


# ---------------------------------------------------------------------------
# API-only launch
# ---------------------------------------------------------------------------


def serve(
    *,
    host: str | None = None,
    port: int | None = None,
    config_path: str | None = None,
    no_web: bool = False,
    kube_api_url: str | None = None,
    kube_token: str | None = None,
    kubeconfig: str | None = None,
    kube_context: str | None = None,
) -> None:
    """Start just the FastAPI/Uvicorn server (blocking).

    When kube credentials are supplied they are stored in module-level
    state so the API server lifespan can inject them as MCP SSE auth
    headers.
    """
    if config_path:
        os.environ["CONFIG"] = config_path
    if no_web:
        os.environ["NO_WEB"] = "1"

    if kube_api_url or kube_token or kubeconfig or kube_context:
        api_url, token = resolve_kube_credentials(
            kube_api_url, kube_token, kubeconfig, kube_context
        )
        if api_url or token:
            set_kube_credentials(api_url, token)

    uvicorn.run(
        "mtv_agent.main:app",
        host=host or settings.server_host,
        port=port or settings.server_port,
    )
