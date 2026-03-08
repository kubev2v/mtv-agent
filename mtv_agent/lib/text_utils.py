"""Shared text-processing helpers used across the agent."""

from pathlib import Path

import yaml

DEFAULT_TRUNCATE_LIMIT = 100_000

DEFAULT_TRUNCATE_HINT = (
    "If the tool supports filtering or limiting results, "
    "use that to get more relevant output."
)


def truncate(
    text: str,
    limit: int = DEFAULT_TRUNCATE_LIMIT,
    hint: str = DEFAULT_TRUNCATE_HINT,
) -> str:
    """Trim oversized text, keeping head and tail for context."""
    if len(text) <= limit:
        return text
    half = limit // 2
    return (
        text[:half]
        + f"\n\n... [truncated {len(text) - limit} chars] ...\n\n"
        + text[-half:]
        + f"\n\n[NOTE: Output was truncated. {hint}]"
    )


def parse_frontmatter(path: Path) -> tuple[dict, str] | None:
    """Read a markdown file with YAML frontmatter and return (meta, body).

    Returns None if the file does not start with ``---``.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None

    _, frontmatter, body = text.split("---", 2)
    meta = yaml.safe_load(frontmatter)
    return meta, body.strip()


def first_sentence(text: str) -> str:
    """Return the first sentence (up to the first period) or the first 120 chars."""
    text = text.strip().split("\n")[0]
    dot = text.find(". ")
    if dot != -1:
        return text[: dot + 1]
    if text.endswith("."):
        return text
    if len(text) > 120:
        return text[:117] + "..."
    return text
