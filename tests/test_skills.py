"""Tests for mtv_agent.server.mcp.skills."""

import tempfile
from pathlib import Path

import pytest

from mtv_agent.server.mcp.skills import SkillsServer
from mtv_agent.server.config import bundled_data_path


@pytest.fixture
def skills_dir():
    with tempfile.TemporaryDirectory() as d:
        skill1 = Path(d) / "my-skill"
        skill1.mkdir()
        (skill1 / "SKILL.md").write_text(
            "---\ndescription: Test skill\n---\n# Hello\nSkill body here."
        )
        skill2 = Path(d) / "another-skill"
        skill2.mkdir()
        (skill2 / "SKILL.md").write_text(
            "---\ndescription: Another one\n---\nMore content."
        )
        yield d


def test_list_tools(skills_dir):
    srv = SkillsServer(skills_dir)
    tools = srv.list_tools()
    assert len(tools) == 2
    names = {t["name"] for t in tools}
    assert "skill_my_skill" in names
    assert "skill_another_skill" in names


def test_tool_description_has_static_hint(skills_dir):
    srv = SkillsServer(skills_dir)
    tools = srv.list_tools()
    for t in tools:
        assert "static" in t["description"].lower()
        assert "once" in t["description"].lower()


@pytest.mark.asyncio
async def test_call_tool(skills_dir):
    srv = SkillsServer(skills_dir)
    result = await srv.call_tool("skill_my_skill", {})
    assert "Skill body here" in result


@pytest.mark.asyncio
async def test_call_unknown_tool(skills_dir):
    srv = SkillsServer(skills_dir)
    result = await srv.call_tool("skill_nonexistent", {})
    assert "Unknown" in result


def test_empty_dir():
    with tempfile.TemporaryDirectory() as d:
        srv = SkillsServer(d)
        assert srv.list_tools() == []


def test_bundled_skills():
    bundled = str(bundled_data_path("skills"))
    srv = SkillsServer(bundled)
    tools = srv.list_tools()
    assert len(tools) == 14
