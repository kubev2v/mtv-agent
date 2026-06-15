"""Async HTTP + SSE client for the mtv-agent API."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10.0
STREAM_TIMEOUT = 600.0


def _raise_with_detail(response: httpx.Response) -> None:
    """Like raise_for_status but includes FastAPI's 'detail' when available."""
    if response.is_success:
        return
    detail = None
    try:
        body = response.json()
        detail = body.get("detail")
    except Exception:
        pass
    if detail:
        raise httpx.HTTPStatusError(detail, request=response.request, response=response)
    response.raise_for_status()


class AgentClient:
    """Talks to the mtv-agent server over HTTP/SSE."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self._base = base_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)

    async def close(self) -> None:
        await self._http.aclose()

    # -- simple REST ---------------------------------------------------------

    async def get_status(self) -> dict:
        r = await self._http.get(f"{self._base}/api/status")
        _raise_with_detail(r)
        return r.json()

    async def get_mcp(self) -> dict:
        r = await self._http.get(f"{self._base}/api/mcp")
        _raise_with_detail(r)
        return r.json()

    async def update_policies(self, data: dict) -> dict:
        r = await self._http.put(f"{self._base}/api/mcp", json=data)
        _raise_with_detail(r)
        return r.json()

    async def set_tool_policy(self, tool_name: str, policy: str) -> dict:
        """Set per-tool policy (accept/ask/reject)."""
        return await self.update_policies({"tool_policies": {tool_name: policy}})

    async def add_bash_prefix(self, prefix: str, accept: bool) -> dict:
        """Add a bash command prefix to accept or reject list."""
        key = "accept_prefixes" if accept else "reject_prefixes"
        return await self.update_policies(
            {"bash_prefix": {"prefix": prefix, "list": key}}
        )

    async def reset_policies(self) -> dict:
        """Reset all policies to defaults."""
        return await self.update_policies({"reset": True})

    async def list_chats(self) -> list[dict]:
        r = await self._http.get(f"{self._base}/api/chats")
        _raise_with_detail(r)
        return r.json()

    async def get_chat(self, chat_id: str) -> dict:
        r = await self._http.get(f"{self._base}/api/chats/{chat_id}")
        _raise_with_detail(r)
        return r.json()

    async def delete_chat(self, chat_id: str) -> None:
        r = await self._http.delete(f"{self._base}/api/chats/{chat_id}")
        _raise_with_detail(r)

    async def cancel_chat(self, session_id: str) -> None:
        r = await self._http.post(f"{self._base}/api/chat/{session_id}/cancel")
        _raise_with_detail(r)

    async def approve_tool(
        self,
        session_id: str,
        approved: bool,
        reason: str | None = None,
    ) -> None:
        body: dict[str, Any] = {"approved": approved}
        if reason:
            body["reason"] = reason
        r = await self._http.post(
            f"{self._base}/api/chat/{session_id}/approve",
            json=body,
        )
        _raise_with_detail(r)

    # -- SSE streaming -------------------------------------------------------

    async def get_commands(self) -> list[dict]:
        r = await self._http.get(f"{self._base}/api/commands")
        _raise_with_detail(r)
        return r.json()

    # -- SSE streaming -------------------------------------------------------

    async def stream_chat(
        self,
        message: str,
        session_id: str | None = None,
        history: list[dict] | None = None,
        namespace: str | None = None,
        command: str | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """POST /api/chat and yield parsed SSE events."""
        body: dict[str, Any] = {"message": message}
        if session_id:
            body["session_id"] = session_id
        if history:
            body["history"] = history
        if namespace:
            body["namespace"] = namespace
        if command:
            body["command"] = command

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(STREAM_TIMEOUT, connect=10.0)
        ) as client:
            async with client.stream(
                "POST",
                f"{self._base}/api/chat",
                json=body,
            ) as resp:
                if not resp.is_success:
                    await resp.aread()
                _raise_with_detail(resp)
                event_type = ""
                data_buf = ""
                async for line in resp.aiter_lines():
                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                    elif line.startswith("data:"):
                        data_buf = line[5:].strip()
                    elif line == "" and event_type:
                        try:
                            data = json.loads(data_buf) if data_buf else {}
                        except json.JSONDecodeError:
                            data = {"raw": data_buf}
                        yield {"event": event_type, **data}
                        event_type = ""
                        data_buf = ""
