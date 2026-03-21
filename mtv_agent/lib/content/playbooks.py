"""Load playbook markdown files and expose them to the API."""

from pathlib import Path

from mtv_agent.lib.text_utils import parse_frontmatter


class Playbook:
    """A single playbook parsed from a markdown file with YAML frontmatter."""

    def __init__(self, name: str, category: str, description: str, body: str) -> None:
        self.name = name
        self.category = category
        self.description = description
        self.body = body


def _parse_playbook(path: Path) -> Playbook | None:
    """Parse a markdown file with YAML frontmatter into a Playbook."""
    parsed = parse_frontmatter(path)
    if parsed is None:
        return None
    meta, body = parsed
    return Playbook(
        name=meta.get("name", path.stem),
        category=meta.get("category", "General"),
        description=meta.get("description", ""),
        body=body,
    )


class PlaybooksManager:
    """Discovers and serves playbook definitions from a directory."""

    def __init__(self) -> None:
        self._playbooks: dict[str, Playbook] = {}

    def load(self, directory: Path) -> None:
        """Load all *.md files from *directory*."""
        directory = Path(directory).expanduser()
        if not directory.is_dir():
            return
        for md_file in sorted(directory.glob("*.md")):
            playbook = _parse_playbook(md_file)
            if playbook:
                self._playbooks[playbook.name] = playbook

    def list_all(self) -> list[dict[str, str]]:
        """Return a list of playbook metadata including body."""
        return [
            {
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "body": p.body,
            }
            for p in self._playbooks.values()
        ]
