"""Persistent chat storage backed by JSON files on disk."""

import json
import logging
import re
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_MAX_TITLE_LEN = 80


class ChatStore:
    """CRUD for chat sessions stored as individual JSON files.

    Each chat is persisted at ``<base_dir>/chats/<chat_id>.json`` with
    the structure: ``{id, title, created_at, updated_at, messages}``.
    """

    def __init__(self, base_dir: str | Path) -> None:
        self._dir = Path(base_dir).expanduser() / "chats"
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, chat_id: str) -> Path:
        return self._dir / f"{chat_id}.json"

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Remove markdown formatting, keeping only plain text."""
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
        text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)
        text = re.sub(r"`(.+?)`", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"^[-*>]+\s+", "", text, flags=re.MULTILINE)
        return text.strip()

    @staticmethod
    def auto_title(messages: list[dict]) -> str:
        """Derive a short title from the first user message."""
        for m in messages:
            if m.get("role") == "user" and m.get("content"):
                text = ChatStore._strip_markdown(m["content"])
                text = text.replace("\n", " ").strip()
                if len(text) > _MAX_TITLE_LEN:
                    return text[:_MAX_TITLE_LEN].rstrip() + "..."
                return text or "New Chat"
        return "New Chat"

    def list_chats(self) -> list[dict]:
        """Return summaries (id, title, updated_at) sorted newest-first."""
        summaries: list[dict] = []
        for p in self._dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                summaries.append(
                    {
                        "id": data["id"],
                        "title": data.get("title", ""),
                        "updated_at": data.get("updated_at", 0),
                    }
                )
            except (json.JSONDecodeError, KeyError, OSError) as exc:
                logger.warning("Skipping corrupt chat file %s: %s", p, exc)
        summaries.sort(key=lambda c: c["updated_at"], reverse=True)
        return summaries

    def load_chat(self, chat_id: str) -> dict | None:
        """Load a full chat (with messages) or ``None`` if not found."""
        p = self._path(chat_id)
        if not p.is_file():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read chat %s: %s", chat_id, exc)
            return None

    def save_chat(
        self,
        chat_id: str,
        messages: list[dict],
        title: str | None = None,
    ) -> dict:
        """Create or update a chat on disk.  Returns the saved record."""
        p = self._path(chat_id)
        now = time.time()

        existing = self.load_chat(chat_id)
        record = {
            "id": chat_id,
            "title": title
            or (existing or {}).get("title")
            or self.auto_title(messages),
            "created_at": (existing or {}).get("created_at", now),
            "updated_at": now,
            "messages": messages,
        }
        p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat file.  Returns ``True`` if it existed."""
        p = self._path(chat_id)
        if p.is_file():
            p.unlink()
            return True
        return False

    def rename_chat(self, chat_id: str, title: str) -> dict | None:
        """Change the title of an existing chat.  Returns updated record."""
        record = self.load_chat(chat_id)
        if record is None:
            return None
        record["title"] = title
        record["updated_at"] = time.time()
        self._path(chat_id).write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return record
