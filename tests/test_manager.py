"""Tests for mtv_agent.server.mcp.manager (policies and routing)."""

import pytest
import pytest_asyncio

from mtv_agent.server.config import bundled_data_path
from mtv_agent.server.mcp.manager import MCPManager, POLICIES_FILE


@pytest_asyncio.fixture
async def mgr():
    backup = None
    if POLICIES_FILE.is_file():
        backup = POLICIES_FILE.read_text()
        POLICIES_FILE.unlink()
    m = MCPManager()
    await m.start(
        mcp_config="/nonexistent",
        skills_dir=str(bundled_data_path("skills")),
    )
    yield m
    await m.stop()
    if POLICIES_FILE.is_file():
        POLICIES_FILE.unlink(missing_ok=True)
    if backup is not None:
        POLICIES_FILE.write_text(backup)


@pytest.mark.asyncio
async def test_start_registers_internal_servers(mgr):
    info = mgr.get_servers()
    names = [s["name"] for s in info["servers"]]
    assert "bash" in names
    assert "skills" in names


@pytest.mark.asyncio
async def test_tool_definitions(mgr):
    tools = mgr.get_tool_definitions()
    names = [t["function"]["name"] for t in tools]
    assert "bash" in names
    assert any(n.startswith("skill_") for n in names)


@pytest.mark.asyncio
async def test_policy_bash_accept_prefix(mgr):
    assert mgr.check_policy("bash", {"command": "ls /tmp"}) == "accept"
    assert mgr.check_policy("bash", {"command": "cat foo.txt"}) == "accept"
    assert mgr.check_policy("bash", {"command": "kubectl get pods"}) == "accept"


@pytest.mark.asyncio
async def test_policy_bash_reject_prefix(mgr):
    assert mgr.check_policy("bash", {"command": "rm -rf /"}) == "reject"
    assert mgr.check_policy("bash", {"command": "shutdown now"}) == "reject"
    assert mgr.check_policy("bash", {"command": "kubectl delete ns foo"}) == "reject"


@pytest.mark.asyncio
async def test_policy_bash_ask_default(mgr):
    assert mgr.check_policy("bash", {"command": "python3 run.py"}) == "ask"


@pytest.mark.asyncio
async def test_policy_skills_accept(mgr):
    assert mgr.check_policy("skill_govc", {}) == "accept"


@pytest.mark.asyncio
async def test_call_bash_tool(mgr):
    result = await mgr.call_tool("bash", {"command": "echo works"})
    assert "works" in result


@pytest.mark.asyncio
async def test_call_skill_tool(mgr):
    result = await mgr.call_tool("skill_mtv_docs", {})
    assert len(result) > 100


@pytest.mark.asyncio
async def test_call_unknown_tool(mgr):
    result = await mgr.call_tool("nonexistent_tool", {})
    assert "Unknown" in result


@pytest.mark.asyncio
async def test_update_policies(mgr):
    mgr.update_policies(
        {
            "servers": {
                "bash": {
                    "policy": {
                        "accept_prefixes": ["ls", "df"],
                        "reject_prefixes": ["rm -rf"],
                    }
                }
            }
        }
    )
    assert mgr.check_policy("bash", {"command": "df -h"}) == "accept"
    assert (
        mgr.check_policy("bash", {"command": "cat foo"}) == "ask"
    )  # no longer accepted
    assert mgr.check_policy("bash", {"command": "rm -rf /"}) == "reject"


@pytest.mark.asyncio
async def test_get_servers_structure(mgr):
    data = mgr.get_servers()
    assert "default_policy" in data
    assert "servers" in data
    for srv in data["servers"]:
        assert "name" in srv
        assert "transport" in srv
        assert "connected" in srv
        assert "policy" in srv
        assert "tools" in srv
