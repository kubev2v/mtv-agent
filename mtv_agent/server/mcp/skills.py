"""Internal 'skills' MCP server -- each SKILL.md becomes a tool."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

STATIC_HINT = (
    " Returns static reference content. "
    "Only call once per conversation -- the result never changes."
)


def _parse_skill(skill_path: Path) -> dict | None:
    """Read a SKILL.md and extract frontmatter + body."""
    text = skill_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    body = parts[2].strip()
    return {"meta": meta, "body": body}


class SkillsServer:
    """Internal MCP-like server exposing skills as tools."""

    name = "skills"
    transport = "internal"
    connected = True

    def __init__(self, skills_dir: str):
        self._skills: dict[str, dict] = {}
        self._load(Path(skills_dir))

    def _load(self, base: Path) -> None:
        if not base.is_dir():
            logger.warning("Skills directory not found: %s", base)
            return
        for skill_dir in sorted(base.iterdir()):
            md = skill_dir / "SKILL.md"
            if not md.is_file():
                continue
            parsed = _parse_skill(md)
            if not parsed:
                continue
            dir_name = skill_dir.name.replace("-", "_")
            tool_name = f"skill_{dir_name}"
            self._skills[tool_name] = parsed
        logger.info("Loaded %d skills as tools", len(self._skills))

    def list_tools(self) -> list[dict]:
        tools = []
        for name, skill in self._skills.items():
            desc = skill["meta"].get("description", name)
            tools.append(
                {
                    "name": name,
                    "description": desc + STATIC_HINT,
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                    },
                }
            )
        return tools

    async def call_tool(self, name: str, _arguments: dict) -> str:
        skill = self._skills.get(name)
        if not skill:
            return f"Unknown skill: {name}"
        return skill["body"]
