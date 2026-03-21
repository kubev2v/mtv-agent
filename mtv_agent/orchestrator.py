"""Orchestrate MCP containers, claude-openai-proxy, and the API server."""

from __future__ import annotations

import atexit
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
from urllib.parse import urlparse

import uvicorn

import mtv_agent.config as config
from mtv_agent.config import (
    _bundled_data_path,
    bundled_config_example,
    bundled_mcp_example,
)
from mtv_agent.lib.kubeconfig import resolve_kube_credentials, set_kube_credentials

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Overridable defaults (MTV_AGENT_* environment variables)
# ---------------------------------------------------------------------------


def _validate_port(env_name: str, default: int) -> int:
    """Read an env var as a TCP port number (1–65535) with a friendly error."""
    raw = os.environ.get(env_name)
    if raw is None:
        return default
    try:
        port = int(raw)
    except ValueError:
        raise SystemExit(f"Error: {env_name}={raw!r} is not a valid integer") from None
    if not 1 <= port <= 65535:
        raise SystemExit(f"Error: {env_name}={port} is outside the valid range 1–65535")
    return port


_COP_PORT = _validate_port("MTV_AGENT_COP_PORT", 1234)
_CONTAINER_PORT = _validate_port("MTV_AGENT_CONTAINER_PORT", 8080)
_KUBE_INSECURE = os.environ.get("MTV_AGENT_KUBE_INSECURE", "true")

_CONTAINER_PREFIX = "mtv-agent-mcp"


def _container_name(key: str) -> str:
    """Derive a container name from an ``mcpServers`` config key."""
    return f"{_CONTAINER_PREFIX}-{key}"


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
        f"{host_port}:{_CONTAINER_PORT}",
        "-e",
        f"MCP_KUBE_INSECURE={_KUBE_INSECURE}",
        image,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    logger.info("  %s -> http://localhost:%d/sse", name, host_port)


def start_mcp_containers(
    runtime: str,
    mcp_raw: dict | None = None,
) -> list[str]:
    """Start MCP server containers, waiting for each to become ready.

    Iterates over ``mcpServers`` in *mcp_raw* (the parsed ``mcp.json``).
    Entries with an ``image`` key get a local container; entries without
    are assumed to be running remotely and are skipped.

    The host port is parsed from the entry's ``url`` field.
    """
    if not mcp_raw:
        return []
    mcp_section = mcp_raw.get("mcpServers", {})
    if not isinstance(mcp_section, dict):
        return []

    logger.info("Starting MCP servers (%s)...", runtime)
    names: list[str] = []
    try:
        for key, entry in mcp_section.items():
            if not isinstance(entry, dict):
                continue
            image = entry.get("image")
            if not image:
                logger.info("  %s -- no image configured, skipping (remote)", key)
                continue
            url = entry.get("url", "")
            host_port = urlparse(url).port or _CONTAINER_PORT
            name = _container_name(key)
            _run_container(runtime, name, image, host_port)
            names.append(name)
            if not _wait_for_port("localhost", host_port, name):
                raise RuntimeError(
                    f"MCP server {name!r} failed to become ready on port {host_port}"
                )
    except Exception:
        if names:
            stop_containers(runtime, names)
        raise
    return names


def stop_containers(runtime: str, names: list[str]) -> None:
    """Stop and remove the given containers."""
    for name in names:
        subprocess.run(
            [runtime, "stop", "--time=2", name],
            capture_output=True,
        )


def stop_mcp_containers_any_runtime() -> None:
    """Best-effort stop of MCP containers using any available runtime."""
    mcp_section = config.mcp_raw_config.get("mcpServers", {})
    names = [_container_name(key) for key in mcp_section]
    for candidate in ("docker", "podman"):
        if not shutil.which(candidate):
            continue
        for name in names:
            subprocess.run(
                [candidate, "stop", name],
                capture_output=True,
            )


# ---------------------------------------------------------------------------
# Claude OpenAI Proxy
# ---------------------------------------------------------------------------


def start_cop() -> subprocess.Popen:
    """Start claude-openai-proxy as a background subprocess."""
    logger.info("Starting claude-openai-proxy on port %d...", _COP_PORT)
    env = {**os.environ, "PORT": str(_COP_PORT)}
    proc = subprocess.Popen(
        [sys.executable, "-m", "claude_openai_proxy"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    logger.info("  claude-openai-proxy -> http://localhost:%d", _COP_PORT)
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
# Config helpers
# ---------------------------------------------------------------------------


def get_default_config_text() -> str:
    """Return the default agent config JSON as a formatted string."""
    return bundled_config_example().read_text(encoding="utf-8")


def _safe_reload_config(
    config_path_arg: str | None = None,
    mcp_config_path_arg: str | None = None,
) -> None:
    """Reload config, converting missing-file errors into clean CLI exits."""
    try:
        config.reload(
            config_path_arg=config_path_arg,
            mcp_config_path_arg=mcp_config_path_arg,
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _require_config_files() -> None:
    """Exit with an error if either config file is missing."""
    if not config.config_path:
        print(
            "Error: config.json not found.\n  Run 'mtv-agent init' to create one.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not config.mcp_config_path:
        print(
            "Error: mcp.json not found.\n  Run 'mtv-agent init' to create one.",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Workspace initialisation
# ---------------------------------------------------------------------------


def init_workspace(target: Path | None = None, *, force: bool = False) -> Path:
    """Copy bundled config, skills, and playbooks into a local workspace.

    Returns the directory that was initialised.  Files that already exist
    are skipped unless *force* is ``True``.
    """
    dest = (target or config.USER_DIR).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []

    # Agent config is user-editable -- only overwrite with --force.
    config_src = bundled_config_example()
    config_dst = dest / "config.json"
    if config_dst.exists() and not force:
        skipped.append("config.json")
    else:
        shutil.copy2(config_src, config_dst)
        created.append("config.json")

    # MCP config is user-editable -- only overwrite with --force.
    mcp_src = bundled_mcp_example()
    mcp_dst = dest / "mcp.json"
    if mcp_dst.exists() and not force:
        skipped.append("mcp.json")
    else:
        shutil.copy2(mcp_src, mcp_dst)
        created.append("mcp.json")

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
    mcp_config_path: str | None = None,
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

    _safe_reload_config(
        config_path_arg=config_path, mcp_config_path_arg=mcp_config_path
    )
    _require_config_files()

    if with_cop:
        _state.cop_proc = start_cop()
        if not _wait_for_port("localhost", _COP_PORT, "claude-openai-proxy"):
            stop_cop(_state.cop_proc)
            _state.cop_proc = None
            print(
                "Error: claude-openai-proxy did not become ready.",
                file=sys.stderr,
            )
            sys.exit(1)

    _state.container_names = start_mcp_containers(rt, mcp_raw=config.mcp_raw_config)

    serve(host=host, port=port, no_web=no_web, kube_api_url=api_url, kube_token=token)


# ---------------------------------------------------------------------------
# API-only launch
# ---------------------------------------------------------------------------


def serve(
    *,
    host: str | None = None,
    port: int | None = None,
    config_path: str | None = None,
    mcp_config_path: str | None = None,
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
    if config_path or mcp_config_path:
        _safe_reload_config(
            config_path_arg=config_path,
            mcp_config_path_arg=mcp_config_path,
        )
    _require_config_files()

    if no_web:
        config.no_web = True

    if kube_api_url or kube_token or kubeconfig or kube_context:
        api_url, token = resolve_kube_credentials(
            kube_api_url, kube_token, kubeconfig, kube_context
        )
        if api_url or token:
            set_kube_credentials(api_url, token)

    uvicorn.run(
        "mtv_agent.main:app",
        host=host or config.settings.server_host,
        port=port or config.settings.server_port,
        timeout_graceful_shutdown=8,
    )
