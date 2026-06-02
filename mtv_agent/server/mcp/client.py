"""Transport-agnostic single-server MCP client (HTTP or stdio)."""

from __future__ import annotations

import logging
from contextlib import AsyncExitStack

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.client.stdio import stdio_client, StdioServerParameters

from mtv_agent.server.config import MCPServerConfig

logger = logging.getLogger(__name__)


class MCPClient:
    """Wraps a single MCP server connection (Streamable HTTP or Stdio)."""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.name = config.name
        self.transport = config.transport
        self._stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None
        self._tools: list[dict] = []
        self.connected = False

    async def connect(self) -> None:
        """Open the transport and initialise the MCP session."""
        stack = AsyncExitStack()
        try:
            if self.config.transport == "stdio":
                if not self.config.command:
                    raise ValueError(f"Stdio server '{self.name}' requires a 'command'")
                params = StdioServerParameters(
                    command=self.config.command,
                    args=self.config.args or [],
                    env=self.config.env,
                )
                ctx = stdio_client(params)
            else:
                if not self.config.url:
                    raise ValueError(f"HTTP server '{self.name}' requires a 'url'")
                http_client = None
                if self.config.headers:
                    http_client = httpx.AsyncClient(headers=self.config.headers)
                ctx = streamable_http_client(
                    self.config.url,
                    http_client=http_client,
                )

            streams = await stack.enter_async_context(ctx)
            read_stream, write_stream = streams[0], streams[1]

            self._session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await self._session.initialize()
            self._stack = stack
            self.connected = True

            resp = await self._session.list_tools()
            self._tools = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "inputSchema": t.inputSchema,
                }
                for t in resp.tools
            ]
            logger.info("MCP '%s' connected – %d tools", self.name, len(self._tools))
        except BaseException:
            self.connected = False
            self._session = None
            try:
                await stack.aclose()
            except BaseException:
                pass
            raise

    async def close(self) -> None:
        if self._stack:
            try:
                await self._stack.aclose()
            except BaseException:
                pass
            self._stack = None
        self._session = None
        self.connected = False

    def list_tools(self) -> list[dict]:
        return self._tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        if not self._session:
            raise RuntimeError(f"MCP '{self.name}' is not connected")
        result = await self._session.call_tool(name, arguments)
        parts = []
        for block in result.content:
            if hasattr(block, "text"):
                parts.append(block.text)
            else:
                parts.append(str(block))
        return "\n".join(parts)
