"""Centralized error formatting for the TUI layer."""

from __future__ import annotations


def friendly_error(exc: Exception) -> str:
    """Turn raw exceptions into short, readable messages."""
    name = type(exc).__name__
    msg = str(exc)

    if "ConnectError" in name or "ConnectionRefused" in msg:
        return "Server is not running (start with: uv run mtv-server)"
    if "TimeoutException" in name or "timed out" in msg.lower():
        return "Request timed out -- the server may be overloaded"
    if "RemoteProtocolError" in name or "Server disconnected" in msg:
        return "Server closed the connection -- check server logs for errors"

    # httpx HTTPStatusError -- extract FastAPI detail if available
    if hasattr(exc, "response"):
        detail = _extract_detail(exc)
        if detail:
            return detail
        return f"Server returned an error ({msg})"

    if "status_code" in msg:
        return f"Server returned an error ({msg})"

    if len(msg) > 120:
        msg = msg[:120] + "..."
    return f"Connection lost: {msg}" if msg else "Connection lost unexpectedly"


def _extract_detail(exc: Exception) -> str | None:
    """Try to pull the 'detail' field from a FastAPI JSON error response."""
    try:
        body = exc.response.json()
        detail = body.get("detail")
        if not detail:
            return None
        if isinstance(detail, str):
            return detail
        return str(detail)
    except Exception:
        pass
    return None
