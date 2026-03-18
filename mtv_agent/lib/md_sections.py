"""Pure-text helpers for extracting sections from Markdown by heading slug."""

import re


def slugify(text: str) -> str:
    """Convert a heading string to a URL-style slug.

    Lowercases, strips non-alphanumeric characters (except hyphens),
    and collapses whitespace/hyphens into single hyphens.
    """
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def extract_section(md: str, fragment: str) -> str:
    """Return the section of *md* whose heading slug matches *fragment*.

    Finds the first heading whose :func:`slugify` output equals
    ``slugify(fragment)``, then returns all lines from that heading up
    to (but not including) the next heading of the same or higher level.

    If no matching heading is found the full text is returned unchanged.
    """
    target = slugify(fragment)
    lines = md.splitlines(keepends=True)

    start: int | None = None
    start_level: int = 0

    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if not m:
            continue
        level, heading = len(m.group(1)), m.group(2)
        if start is None and slugify(heading) == target:
            start, start_level = i, level
        elif start is not None and level <= start_level:
            return "".join(lines[start:i])

    if start is not None:
        return "".join(lines[start:])

    return md
