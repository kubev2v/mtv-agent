"""Manages multiple named MCP SSE connections with tool-name routing."""

from __future__ import annotations

import logging

from mtv_agent.config import MCPServerConfig
from mtv_agent.lib.mcp_client import MCPClient, _CONNECTION_ERRORS

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages multiple named MCP SSE connections with tool-name routing.

    Keeps a registry of all *configured* servers (from the config file) so
    that clients can list available servers and connect/disconnect by name
    without providing URLs.
    """

    def __init__(self) -> None:
        self._configs: dict[str, MCPServerConfig] = {}
        self._clients: dict[str, MCPClient] = {}
        self._tool_map: dict[str, str] = {}

    def load_configs(self, servers: dict[str, MCPServerConfig]) -> None:
        """Store the full set of configured servers (does not connect)."""
        self._configs.update(servers)

    async def connect_all(self, servers: dict[str, MCPServerConfig]) -> None:
        """Store configs and open SSE connections to every server.

        Servers that are unreachable are logged and skipped so the
        application can still start.  They remain in ``_configs`` and
        can be connected later via ``connect_one``.
        """
        self.load_configs(servers)
        for name, cfg in servers.items():
            client = MCPClient()
            try:
                await client.connect(cfg.url, headers=cfg.headers or None)
                self._clients[name] = client
            except _CONNECTION_ERRORS as exc:
                logger.warning(
                    "Could not connect to MCP server %r at %s: %s. "
                    "Skipping -- reconnect via the UI or restart later.",
                    name,
                    cfg.url,
                    exc,
                )
            except Exception as exc:
                logger.warning(
                    "Unexpected error connecting to MCP server %r at %s: %s. "
                    "Skipping -- reconnect via the UI or restart later.",
                    name,
                    cfg.url,
                    exc,
                )

    async def list_tools(self) -> list[dict]:
        """Aggregate tool definitions from all connected servers."""
        all_tools: list[dict] = []
        self._tool_map.clear()
        for server_name, client in self._clients.items():
            for tool in await client.list_tools():
                tool_name = tool["function"]["name"]
                if tool_name in self._tool_map:
                    logger.warning(
                        "Tool %r from server %r shadows the same tool from %r",
                        tool_name,
                        server_name,
                        self._tool_map[tool_name],
                    )
                self._tool_map[tool_name] = server_name
                all_tools.append(tool)
        return all_tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Route a tool call to the server that provides it."""
        server_name = self._tool_map.get(name)
        if not server_name:
            return f"Unknown MCP tool: {name}"
        try:
            return await self._clients[server_name].call_tool(name, arguments)
        except _CONNECTION_ERRORS as exc:
            logger.error("MCP tool %r failed after reconnect: %s", name, exc)
            return f"MCP server error: {exc}"
        except Exception as exc:
            logger.error("MCP tool %r raised %s: %s", name, type(exc).__name__, exc)
            return f"Tool error: {exc}"

    async def connect_one(self, name: str) -> bool:
        """Connect a configured server by name. Returns False if unknown."""
        cfg = self._configs.get(name)
        if cfg is None:
            return False
        if name in self._clients:
            await self._clients[name].disconnect()
        client = MCPClient()
        await client.connect(cfg.url, headers=cfg.headers or None)
        self._clients[name] = client
        return True

    async def disconnect_one(self, name: str) -> bool:
        """Disconnect a single server. Returns True if it was connected."""
        client = self._clients.pop(name, None)
        if client is None:
            return False
        await client.disconnect()
        self._tool_map = {k: v for k, v in self._tool_map.items() if v != name}
        return True

    def get_server_info(self) -> list[dict]:
        """Return [{name, url, connected}, ...] for every configured server."""
        return [
            {
                "name": name,
                "url": cfg.url,
                "connected": name in self._clients,
            }
            for name, cfg in self._configs.items()
        ]

    async def disconnect_all(self) -> None:
        """Tear down every SSE connection."""
        for client in self._clients.values():
            await client.disconnect()
        self._clients.clear()
        self._tool_map.clear()

    @property
    def server_names(self) -> list[str]:
        return list(self._clients)
