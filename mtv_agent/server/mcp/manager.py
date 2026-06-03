"""Unified MCP manager -- external clients + internal servers + policies."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from mtv_agent.server.config import bundled_policies_example, load_mcp_servers
from mtv_agent.server.mcp.bash import BashServer
from mtv_agent.server.mcp.client import MCPClient
from mtv_agent.server.mcp.skills import SkillsServer

logger = logging.getLogger(__name__)

POLICIES_FILE = Path.home() / ".mtv-agent" / "policies.json"


# ---------------------------------------------------------------------------
# Policy model
# ---------------------------------------------------------------------------


@dataclass
class ServerPolicy:
    default: str = "ask"
    tools: dict[str, str] = field(default_factory=dict)
    accept_prefixes: list[str] = field(default_factory=list)
    reject_prefixes: list[str] = field(default_factory=list)


def _load_default_policies() -> dict:
    """Load the bundled policies.json.example as the source of truth for defaults."""
    path = bundled_policies_example()
    with open(path) as f:
        return json.load(f)


def _parse_server_policy(data: dict) -> ServerPolicy:
    return ServerPolicy(
        default=data.get("default", "ask"),
        tools=data.get("tools", {}),
        accept_prefixes=list(data.get("accept_prefixes", [])),
        reject_prefixes=list(data.get("reject_prefixes", [])),
    )


# ---------------------------------------------------------------------------
# Server protocol -- both MCPClient and internal servers implement this
# ---------------------------------------------------------------------------


@runtime_checkable
class ToolServer(Protocol):
    name: str
    transport: str
    connected: bool

    def list_tools(self) -> list[dict]: ...
    async def call_tool(self, name: str, arguments: dict) -> str: ...


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


class MCPManager:
    """Aggregates all tool servers, routes calls, and manages policies."""

    def __init__(self) -> None:
        self._servers: dict[str, ToolServer] = {}
        self._tool_to_server: dict[str, ToolServer] = {}
        self._policies: dict[str, ServerPolicy] = {}
        self._default_policy = "ask"

    # -- lifecycle -----------------------------------------------------------

    async def start(
        self,
        mcp_config: str | None = None,
        skills_dir: str = "",
    ) -> None:
        """Connect all servers (internal + external from mcp.json)."""
        self._apply_default_policies()

        bash = BashServer()
        self._register(bash)

        skills = SkillsServer(skills_dir)
        self._register(skills)

        configs = load_mcp_servers(mcp_config)
        failed: list[str] = []
        for cfg in configs:
            client = MCPClient(cfg)
            try:
                await client.connect()
                self._register(client)
            except BaseException as exc:
                if cfg.transport == "stdio":
                    hint = f"command: {cfg.command} {' '.join(cfg.args)}"
                else:
                    hint = f"url: {cfg.url}"
                failed.append(f"  - {cfg.name} ({hint})\n    {exc}")
        if failed:
            details = "\n".join(failed)
            raise RuntimeError(
                f"Failed to connect to MCP server(s):\n\n"
                f"{details}\n\n"
                f"Check mcp.json and verify the servers are installed and reachable.\n"
                f"For stdio servers, ensure the command is on your PATH.\n"
                f"For HTTP servers, ensure the URL is correct and the server is running."
            )

        self._load_policies()

    async def stop(self) -> None:
        for srv in self._servers.values():
            if isinstance(srv, MCPClient):
                await srv.close()
        self._servers.clear()
        self._tool_to_server.clear()

    def _register(self, server: ToolServer) -> None:
        self._servers[server.name] = server
        for tool in server.list_tools():
            self._tool_to_server[tool["name"]] = server
        self._policies.setdefault(server.name, ServerPolicy())

    def _apply_default_policies(self) -> None:
        """Seed policies from the bundled policies.json.example."""
        defaults = _load_default_policies()
        self._default_policy = defaults.get("default_policy", "ask")
        for srv_name, pol_data in defaults.get("servers", {}).items():
            self._policies[srv_name] = _parse_server_policy(pol_data)

    # -- tool operations -----------------------------------------------------

    def get_tool_definitions(self) -> list[dict]:
        """OpenAI-format tool definitions for the LLM."""
        defs = []
        for srv in self._servers.values():
            if not srv.connected:
                continue
            for tool in srv.list_tools():
                defs.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool.get("description", ""),
                            "parameters": tool.get("inputSchema", {}),
                        },
                    }
                )
        return defs

    async def call_tool(self, name: str, arguments: dict) -> str:
        server = self._tool_to_server.get(name)
        if not server:
            return f"Unknown tool: {name}"
        return await server.call_tool(name, arguments)

    # -- policy operations ---------------------------------------------------

    def check_policy(self, tool_name: str, arguments: dict) -> str:
        server = self._tool_to_server.get(tool_name)
        if not server:
            return self._default_policy
        policy = self._policies.get(server.name, ServerPolicy())

        if tool_name in policy.tools:
            return policy.tools[tool_name]

        if server.name == "bash":
            cmd = arguments.get("command", "").strip()
            for prefix in policy.reject_prefixes:
                if cmd.startswith(prefix):
                    return "reject"
            for prefix in policy.accept_prefixes:
                if cmd.startswith(prefix):
                    return "accept"

        return policy.default or self._default_policy

    # -- API model (GET /api/mcp) -------------------------------------------

    def get_servers(self) -> dict[str, Any]:
        """Build the full response for GET /api/mcp."""
        servers = []
        for srv in self._servers.values():
            policy = self._policies.get(srv.name, ServerPolicy())
            entry: dict[str, Any] = {
                "name": srv.name,
                "transport": srv.transport,
                "connected": srv.connected,
                "policy": {
                    "default": policy.default,
                },
                "tools": srv.list_tools(),
            }
            if isinstance(srv, MCPClient):
                if srv.config.transport == "http":
                    entry["url"] = srv.config.url
                else:
                    entry["command"] = srv.config.command
            if policy.tools:
                entry["policy"]["tools"] = policy.tools
            if policy.accept_prefixes:
                entry["policy"]["accept_prefixes"] = policy.accept_prefixes
            if policy.reject_prefixes:
                entry["policy"]["reject_prefixes"] = policy.reject_prefixes
            servers.append(entry)
        return {"default_policy": self._default_policy, "servers": servers}

    # -- API model (PUT /api/mcp) -------------------------------------------

    def update_policies(self, data: dict) -> None:
        """Update policies from client data and persist."""
        if data.get("reset"):
            self._reset_policies()
            return

        if "default_policy" in data:
            self._default_policy = data["default_policy"]

        for tool_name, policy_val in data.get("tool_policies", {}).items():
            server = self._tool_to_server.get(tool_name)
            if server and server.name in self._policies:
                self._policies[server.name].tools[tool_name] = policy_val

        bp = data.get("bash_prefix")
        if bp and "bash" in self._policies:
            prefix = bp["prefix"]
            target_list = bp["list"]
            bash_policy = self._policies["bash"]
            if target_list == "accept_prefixes":
                if prefix not in bash_policy.accept_prefixes:
                    bash_policy.accept_prefixes.append(prefix)
                if prefix in bash_policy.reject_prefixes:
                    bash_policy.reject_prefixes.remove(prefix)
            elif target_list == "reject_prefixes":
                if prefix not in bash_policy.reject_prefixes:
                    bash_policy.reject_prefixes.append(prefix)
                if prefix in bash_policy.accept_prefixes:
                    bash_policy.accept_prefixes.remove(prefix)

        for srv_name, srv_data in data.get("servers", {}).items():
            if srv_name not in self._policies:
                continue
            pol_data = srv_data.get("policy", {})
            policy = self._policies[srv_name]
            if "default" in pol_data:
                policy.default = pol_data["default"]
            if "tools" in pol_data:
                policy.tools.update(pol_data["tools"])
            if "accept_prefixes" in pol_data:
                policy.accept_prefixes = pol_data["accept_prefixes"]
            if "reject_prefixes" in pol_data:
                policy.reject_prefixes = pol_data["reject_prefixes"]
        self._save_policies()

    def _reset_policies(self) -> None:
        """Reset all policies to bundled defaults."""
        self._policies.clear()
        self._apply_default_policies()
        for name in self._servers:
            if name not in self._policies:
                self._policies[name] = ServerPolicy()
        if POLICIES_FILE.is_file():
            try:
                POLICIES_FILE.unlink()
            except OSError:
                pass
        logger.info("Policies reset to defaults")

    # -- persistence ---------------------------------------------------------

    def _save_policies(self) -> None:
        try:
            POLICIES_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "default_policy": self._default_policy,
                "servers": {},
            }
            for name, policy in self._policies.items():
                entry: dict[str, Any] = {"default": policy.default}
                if policy.tools:
                    entry["tools"] = policy.tools
                if policy.accept_prefixes:
                    entry["accept_prefixes"] = policy.accept_prefixes
                if policy.reject_prefixes:
                    entry["reject_prefixes"] = policy.reject_prefixes
                data["servers"][name] = entry
            POLICIES_FILE.write_text(json.dumps(data, indent=2))
            logger.info("Policies saved to %s", POLICIES_FILE)
        except OSError as exc:
            logger.warning("Could not save policies: %s", exc)

    def _load_policies(self) -> None:
        if not POLICIES_FILE.is_file():
            return
        try:
            data = json.loads(POLICIES_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return
        if "default_policy" in data:
            self._default_policy = data["default_policy"]
        for srv_name, pol_data in data.get("servers", {}).items():
            if srv_name not in self._policies:
                self._policies[srv_name] = ServerPolicy()
            policy = self._policies[srv_name]
            policy.default = pol_data.get("default", policy.default)
            policy.tools = pol_data.get("tools", policy.tools)
            policy.accept_prefixes = pol_data.get(
                "accept_prefixes", policy.accept_prefixes
            )
            policy.reject_prefixes = pol_data.get(
                "reject_prefixes", policy.reject_prefixes
            )
        logger.info("Policies loaded from %s", POLICIES_FILE)
