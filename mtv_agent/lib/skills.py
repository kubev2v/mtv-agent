"""Load skill markdown files and expose them as context for the agent."""

from pathlib import Path

from mtv_agent.lib.text_utils import parse_frontmatter


class Skill:
    """A single skill parsed from a SKILL.md file."""

    def __init__(self, name: str, description: str, body: str) -> None:
        self.name = name
        self.description = description
        self.body = body


def _parse_skill(path: Path) -> Skill | None:
    """Parse a SKILL.md file with YAML frontmatter into a Skill."""
    parsed = parse_frontmatter(path)
    if parsed is None:
        return None
    meta, body = parsed
    return Skill(
        name=meta.get("name", path.parent.name),
        description=meta.get("description", ""),
        body=body,
    )


class SkillsManager:
    """Discovers and serves skill definitions from a directory tree."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def load(self, directory: Path) -> None:
        """Walk *directory* looking for <name>/SKILL.md files."""
        directory = directory.expanduser()
        if not directory.is_dir():
            return
        for skill_file in sorted(directory.glob("*/SKILL.md")):
            skill = _parse_skill(skill_file)
            if skill:
                self._skills[skill.name] = skill

    def get_catalog(self) -> str:
        """Return a concise catalog of skill names and descriptions."""
        lines = []
        for skill in self._skills.values():
            lines.append(f"- {skill.name}: {skill.description}")
        return "\n".join(lines)

    def get_body(self, name: str) -> str | None:
        """Return the raw skill body, or None if not found."""
        skill = self._skills.get(name)
        if not skill:
            return None
        return skill.body

    def resolve(self, raw: str) -> str | None:
        """Match a raw string against known skill names (case-insensitive).

        Returns the canonical skill name, or None.
        """
        cleaned = raw.strip().lower().strip("\"'`., \n")
        if cleaned in ("none", ""):
            return None
        for name in self._skills:
            if cleaned == name.lower():
                return name
        return None

    @property
    def names(self) -> set[str]:
        return set(self._skills)

    def list_all(self) -> list[dict[str, str]]:
        """Return a list of {name, description} dicts for all skills."""
        return [
            {"name": s.name, "description": s.description}
            for s in self._skills.values()
        ]
