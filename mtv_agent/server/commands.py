"""Command loader -- each .md file becomes a slash command."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def _parse_command(path: Path) -> dict | None:
    """Read a command .md and extract frontmatter + body."""
    text = path.read_text(encoding="utf-8")
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
    return {
        "name": meta.get("name", path.stem),
        "description": meta.get("description", "").strip(),
        "category": meta.get("category", ""),
        "body": body,
    }


def load_commands(commands_dir: str) -> dict[str, dict]:
    """Load all commands from a directory.

    Returns a dict mapping command name to command data.
    """
    base = Path(commands_dir)
    commands: dict[str, dict] = {}
    if not base.is_dir():
        logger.warning("Commands directory not found: %s", base)
        return commands
    for md in sorted(base.glob("*.md")):
        parsed = _parse_command(md)
        if not parsed:
            continue
        commands[parsed["name"]] = parsed
    logger.info("Loaded %d commands", len(commands))
    return commands
