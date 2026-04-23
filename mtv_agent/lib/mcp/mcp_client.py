"""MCP Streamable HTTP client -- connect, discover tools, and call them."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from contextlib import AsyncExitStack

import anyio
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent

logger = logging.getLogger(__name__)

_CONNECTION_ERRORS = (
    TimeoutError,
    anyio.ClosedResourceError,
    anyio.BrokenResourceError,
    anyio.EndOfStream,
    httpx.ReadTimeout,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
)

MAX_RECONNECT_ATTEMPTS = 3
DEFAULT_TOOL_CALL_TIMEOUT = 360  # seconds


class MCPClient:
    """Manages a persistent Streamable HTTP connection to an MCP server.

    Each connection runs in a dedicated background task so the anyio
    cancel-scope created by ``streamable_http_client`` is tied to that
    task, not to the caller (e.g. the FastAPI lifespan handler).  This
    prevents ``CancelledError`` from leaking into the lifespan when a
    connection is torn down from a request handler.
    """

    def __init__(self, tool_timeout: int = DEFAULT_TOOL_CALL_TIMEOUT) -> None:
        self._tool_timeout = tool_timeout
        self._session: ClientSession | None = None
        self._url: str | None = None
        self._headers: dict[str, str] | None = None
        self._task: asyncio.Task | None = None
        self._ready: asyncio.Event | None = None
        self._stop: asyncio.Event | None = None
        self._connect_error: BaseException | None = None

    async def connect(self, url: str, headers: dict[str, str] | None = None) -> None:
        """Establish a Streamable HTTP session and initialize the MCP handshake."""
        await self.disconnect()
        self._url = url
        self._headers = headers
        self._ready = asyncio.Event()
        self._stop = asyncio.Event()
        self._connect_error = None
        self._task = asyncio.create_task(self._run())
        await self._ready.wait()
        if self._connect_error is not None:
            raise self._connect_error

    async def _run(self) -> None:
        """Background task owning the Streamable HTTP transport lifetime."""
        assert self._ready is not None and self._stop is not None
        try:
            async with AsyncExitStack() as stack:
                http_client = httpx.AsyncClient(
                    headers=self._headers or {},
                    timeout=httpx.Timeout(30, read=60 * 60 * 24),
                )
                await stack.enter_async_context(http_client)
                read_stream, write_stream, _ = await stack.enter_async_context(
                    streamable_http_client(
                        self._url,
                        http_client=http_client,
                    )
                )
                session = await stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                await session.initialize()
                self._session = session
                self._ready.set()
                await self._stop.wait()
        except BaseException as exc:
            if not self._ready.is_set():
                self._connect_error = exc
        finally:
            self._session = None
            self._ready.set()

    async def _reconnect(self) -> None:
        """Attempt to re-establish the Streamable HTTP connection."""
        logger.info("Reconnecting MCP client to %s …", self._url)
        url, headers = self._url, self._headers
        await self.disconnect()
        await self.connect(url, headers)
        logger.info("Reconnected to %s", self._url)

    async def list_tools(self) -> list[dict]:
        """Return tool definitions in OpenAI-compatible function format."""
        for attempt in range(1, MAX_RECONNECT_ATTEMPTS + 1):
            if not self._session:
                if attempt >= MAX_RECONNECT_ATTEMPTS:
                    raise RuntimeError("Not connected -- call connect() first")
                logger.warning(
                    "Session gone, reconnecting (attempt %d/%d)",
                    attempt,
                    MAX_RECONNECT_ATTEMPTS,
                )
                await self._reconnect()
                continue
            try:
                result = await self._session.list_tools()
                break
            except _CONNECTION_ERRORS as exc:
                if attempt >= MAX_RECONNECT_ATTEMPTS:
                    raise
                logger.warning(
                    "MCP list_tools failed (%s), reconnecting (attempt %d/%d)",
                    exc,
                    attempt,
                    MAX_RECONNECT_ATTEMPTS,
                )
                await self._reconnect()
        else:
            raise RuntimeError("MCP list_tools exhausted reconnect attempts")
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
            for tool in result.tools
        ]

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Invoke a tool, reconnecting if the session is dead or hung."""
        for attempt in range(1, MAX_RECONNECT_ATTEMPTS + 1):
            if not self._session:
                if attempt >= MAX_RECONNECT_ATTEMPTS:
                    raise RuntimeError("Not connected -- call connect() first")
                logger.warning(
                    "Session gone, reconnecting (attempt %d/%d)",
                    attempt,
                    MAX_RECONNECT_ATTEMPTS,
                )
                await self._reconnect()
                continue
            try:
                t0 = time.perf_counter()
                async with asyncio.timeout(self._tool_timeout):
                    result = await self._session.call_tool(name, arguments)
                elapsed = time.perf_counter() - t0
                logger.debug("MCP call_tool(%s) round-trip: %.3fs", name, elapsed)
                break
            except _CONNECTION_ERRORS as exc:
                if attempt >= MAX_RECONNECT_ATTEMPTS:
                    raise
                logger.warning(
                    "MCP call_tool(%s) failed (%s), reconnecting (attempt %d/%d)",
                    name,
                    exc,
                    attempt,
                    MAX_RECONNECT_ATTEMPTS,
                )
                await self._reconnect()
        else:
            raise RuntimeError("MCP call_tool exhausted reconnect attempts")

        parts = []
        for block in result.content:
            if isinstance(block, TextContent):
                parts.append(block.text)
            else:
                parts.append(str(block))
        text = "\n".join(parts)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, (dict, list)):
                return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        return text

    @property
    def url(self) -> str | None:
        return self._url

    async def disconnect(self) -> None:
        """Tear down the connection (preserves url/headers for reconnect)."""
        if self._task is not None and not self._task.done():
            if self._stop is not None:
                self._stop.set()
            try:
                await asyncio.wait_for(self._task, timeout=3.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                self._task.cancel()
                try:
                    await self._task
                except (asyncio.CancelledError, Exception):
                    pass
                # Propagate if disconnect() itself was cancelled by the caller.
                current = asyncio.current_task()
                if current is not None and current.cancelling() > 0:
                    raise asyncio.CancelledError()
        self._task = None
        self._session = None
