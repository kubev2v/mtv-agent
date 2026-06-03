"""Dump HTTP traffic between the agent and the inference server as JSON.

When enabled, captures every httpx request/response via event hooks and
writes them as ``.json`` files with HTTP headers stored as metadata and
pretty-printed JSON bodies for easy reading and syntax highlighting.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LLMDumper:
    """Captures HTTP traffic and writes JSON dump files.

    Attach :meth:`on_request` / :meth:`on_response` as httpx event hooks.
    Call :meth:`set_session` once per chat session and :meth:`next_iteration`
    before each LLM call so files are numbered correctly.
    """

    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir).expanduser()
        self._session_dir: Path | None = None
        self._iteration = 0
        self._pending_request: dict[str, Any] | None = None

    def set_session(self, session_id: str) -> None:
        """Set the output subdirectory for a new chat session."""
        self._session_dir = self._base_dir / session_id
        self._session_dir.mkdir(parents=True, exist_ok=True)
        self._iteration = 0

    def next_iteration(self) -> None:
        """Advance the iteration counter (call before each LLM request)."""
        self._iteration += 1

    async def on_request(self, request: httpx.Request) -> None:
        """httpx event hook -- capture the outgoing HTTP request."""
        self._pending_request = _format_request(request)

    async def on_response(self, response: httpx.Response) -> None:
        """httpx event hook -- capture the HTTP response and flush both files."""
        await response.aread()

        if not self._session_dir:
            return

        prefix = f"agent_loop_{self._iteration:02d}"

        if self._pending_request is not None:
            _write(self._session_dir / f"{prefix}_request.json", self._pending_request)
            self._pending_request = None

        _write(
            self._session_dir / f"{prefix}_response.json",
            _format_response(response),
        )


def _format_request(request: httpx.Request) -> dict[str, Any]:
    """Build a JSON-serialisable dict from an httpx Request."""
    headers = {}
    for name, value in request.headers.items():
        if name.lower() == "authorization":
            value = "Bearer ***"
        headers[name] = value

    return {
        "type": "request",
        "method": request.method,
        "path": request.url.raw_path.decode(),
        "headers": headers,
        "body": _parse_body(request.content),
    }


def _format_response(response: httpx.Response) -> dict[str, Any]:
    """Build a JSON-serialisable dict from an httpx Response."""
    headers = dict(response.headers.items())

    return {
        "type": "response",
        "status": response.status_code,
        "reason": _reason_phrase(response.status_code),
        "headers": headers,
        "body": _parse_body(response.content),
    }


def _parse_body(raw: bytes) -> Any:
    """Try to parse *raw* as JSON; fall back to a plain string."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return raw.decode("utf-8", errors="replace")


def _reason_phrase(status_code: int) -> str:
    """Return the standard HTTP reason phrase for common status codes."""
    return {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }.get(status_code, "")


def _write(path: Path, data: dict[str, Any]) -> None:
    """Write a JSON dump file, logging errors instead of raising."""
    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:
        logger.warning("Failed to write dump file %s", path)
