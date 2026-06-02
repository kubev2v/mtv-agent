"""Tests for mtv_agent.server.mcp.bash."""

import pytest

from mtv_agent.server.mcp.bash import BashServer


@pytest.fixture
def bash():
    return BashServer()


def test_list_tools(bash):
    tools = bash.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "bash"
    assert "command" in tools[0]["inputSchema"]["properties"]


@pytest.mark.asyncio
async def test_call_tool_echo(bash):
    result = await bash.call_tool("bash", {"command": "echo hello"})
    assert result.strip() == "hello"


@pytest.mark.asyncio
async def test_call_tool_empty(bash):
    result = await bash.call_tool("bash", {"command": ""})
    assert "empty" in result.lower()


@pytest.mark.asyncio
async def test_call_tool_exit_code(bash):
    result = await bash.call_tool("bash", {"command": "exit 1"})
    assert isinstance(result, str)
