"""Unified tool registry that combines MCP tools and built-ins."""

import logging
from pathlib import Path

from mtv_agent.lib import bash_tool, web_tool
from mtv_agent.lib.mcp_manager import MCPManager
from mtv_agent.lib.skills import SkillsManager

logger = logging.getLogger(__name__)


def _check_flags(arguments: dict) -> str | None:
    """Return an error string if ``flags`` is not a dict, else None."""
    flags = arguments.get("flags")
    if flags is None or isinstance(flags, dict):
        return None
    return (
        f"Invalid 'flags' parameter: expected a JSON object, got {type(flags).__name__}.\n"
        f"You passed: flags={flags!r}\n"
        'Correct usage example: {"command": "get provider", "flags": {"namespace": "my-ns"}}\n'
        'Please retry with flags as a JSON object like {"key": "value"}.'
    )


class ToolRegistry:
    """Single entry point for tool definitions and execution."""

    def __init__(
        self,
        mcp: MCPManager | None,
        skills: SkillsManager,
        bash_timeout: int = 360,
        cache_dir: str | Path | None = None,
    ) -> None:
        self._mcp = mcp
        self._skills = skills
        self._bash_timeout = bash_timeout
        self._cache_dir = cache_dir
        self._mcp_tools: list[dict] = []

    @property
    def skills(self) -> SkillsManager:
        return self._skills

    async def refresh(self) -> None:
        """(Re)load tool definitions from all sources."""
        if self._mcp:
            self._mcp_tools = await self._mcp.list_tools()

    def get_tool_definitions(self) -> list[dict]:
        """Return the combined list of tools for the LLM (no skills)."""
        return [bash_tool.TOOL_DEFINITION, web_tool.TOOL_DEFINITION] + self._mcp_tools

    async def execute_tool(self, name: str, arguments: dict) -> str:
        """Route a tool call to the right backend and return the result."""
        if name == bash_tool.TOOL_NAME:
            return await bash_tool.run(
                arguments.get("command", ""), timeout=self._bash_timeout
            )

        if name == web_tool.TOOL_NAME:
            return await web_tool.run(
                arguments.get("url", ""), cache_dir=self._cache_dir
            )

        if self._mcp:
            error = _check_flags(arguments)
            if error:
                logger.warning(
                    "Malformed flags for tool %s: %r", name, arguments.get("flags")
                )
                return error
            return await self._mcp.call_tool(name, arguments)

        return f"Unknown tool: {name}"
