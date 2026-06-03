"""Workspace initialisation -- copies bundled data to ~/.mtv-agent/."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from mtv_agent.server.config import (
    USER_DIR,
    bundled_config_example,
    bundled_data_path,
    bundled_mcp_example,
    bundled_policies_example,
)

logger = logging.getLogger(__name__)


def init_workspace(target: Path | None = None, *, force: bool = False) -> Path:
    """Copy bundled config, skills, and commands into a local workspace.

    Returns the directory that was initialised.  Config files that already
    exist are skipped unless *force* is ``True``.  Skills and commands are
    always refreshed so users get updates on new versions.
    """
    dest = (target or USER_DIR).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []

    config_src = bundled_config_example()
    config_dst = dest / "config.json"
    if config_dst.exists() and not force:
        skipped.append("config.json")
    else:
        shutil.copy2(config_src, config_dst)
        created.append("config.json")

    mcp_src = bundled_mcp_example()
    mcp_dst = dest / "mcp.json"
    if mcp_dst.exists() and not force:
        skipped.append("mcp.json")
    else:
        shutil.copy2(mcp_src, mcp_dst)
        created.append("mcp.json")

    policies_src = bundled_policies_example()
    policies_dst = dest / "policies.json"
    if policies_dst.exists() and not force:
        skipped.append("policies.json")
    else:
        shutil.copy2(policies_src, policies_dst)
        created.append("policies.json")

    skills_src = bundled_data_path("skills")
    skills_dst = dest / "skills"
    if skills_dst.exists():
        shutil.rmtree(skills_dst)
    shutil.copytree(skills_src, skills_dst)
    created.append("skills/")

    commands_src = bundled_data_path("commands")
    commands_dst = dest / "commands"
    if commands_dst.exists():
        shutil.rmtree(commands_dst)
    shutil.copytree(commands_src, commands_dst)
    created.append("commands/")

    logger.info("Initialised workspace: %s", dest)
    if created:
        logger.info("  created/updated: %s", ", ".join(created))
    if skipped:
        logger.info("  skipped (already exist): %s", ", ".join(skipped))

    return dest
