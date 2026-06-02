"""JSON-file backed chat persistence."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _first_sentence(text: str, limit: int = 80) -> str:
    """Extract a short title from the first user message."""
    line = text.strip().split("\n")[0]
    if len(line) > limit:
        return line[:limit] + "..."
    return line


class ChatStore:
    """Stores chat histories as individual JSON files on disk."""

    def __init__(self, cache_dir: str = "~/.mtv-agent/cache"):
        self._dir = Path(cache_dir).expanduser()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, chat_id: str) -> Path:
        return self._dir / f"{chat_id}.json"

    def list(self) -> list[dict[str, Any]]:
        """Return summaries of all saved chats, newest first."""
        chats = []
        for f in self._dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                chats.append(
                    {
                        "id": f.stem,
                        "title": data.get("title", f.stem),
                        "created": data.get("created", 0),
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except (json.JSONDecodeError, OSError):
                continue
        chats.sort(key=lambda c: c["created"], reverse=True)
        return chats

    def get(self, chat_id: str) -> dict[str, Any] | None:
        """Load a full chat by ID."""
        path = self._path(chat_id)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def save(
        self,
        chat_id: str,
        messages: list[dict],
        title: str | None = None,
    ) -> None:
        """Save a chat. Auto-generates a title from the first user message."""
        existing = self.get(chat_id)
        if not title:
            first_user = next(
                (m["content"] for m in messages if m.get("role") == "user"),
                chat_id,
            )
            title = _first_sentence(first_user)
        data = {
            "id": chat_id,
            "title": title,
            "created": existing["created"] if existing else time.time(),
            "updated": time.time(),
            "messages": messages,
        }
        self._path(chat_id).write_text(json.dumps(data, indent=2))

    def delete(self, chat_id: str) -> bool:
        path = self._path(chat_id)
        if path.is_file():
            path.unlink()
            return True
        return False
