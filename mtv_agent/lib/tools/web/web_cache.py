"""Disk-based URL cache with TTL for the web_fetch tool."""

import hashlib
import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TTL = 3600  # 1 hour


class WebCache:
    """Simple URL-to-markdown disk cache keyed by SHA-256 of the URL."""

    def __init__(self, cache_dir: str | Path, ttl: int = DEFAULT_TTL) -> None:
        self._dir = Path(cache_dir).expanduser() / "web"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl

    @staticmethod
    def _key(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def _path(self, url: str) -> Path:
        return self._dir / f"{self._key(url)}.json"

    def _invalidate(self, p: Path, url: str, reason: str) -> None:
        """Remove a cache file and log why."""
        try:
            p.unlink()
        except OSError:
            pass
        logger.debug("web_cache: %s %s", reason, url)

    def get(self, url: str) -> str | None:
        """Return cached markdown for *url* if fresh, else ``None``."""
        p = self._path(url)
        if not p.is_file():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._invalidate(p, url, "malformed")
            return None
        fetched_at = data.get("fetched_at")
        markdown = data.get("markdown")
        if not isinstance(fetched_at, (int, float)):
            self._invalidate(p, url, "invalid fetched_at")
            return None
        if time.time() - fetched_at > self._ttl:
            self._invalidate(p, url, "expired")
            return None
        if not isinstance(markdown, str):
            self._invalidate(p, url, "invalid markdown")
            return None
        logger.info("web_cache: hit %s", url)
        return markdown

    def put(self, url: str, markdown: str) -> None:
        """Store *markdown* for *url* on disk."""
        record = {
            "fetched_at": time.time(),
            "markdown": markdown,
        }
        try:
            self._path(url).write_text(
                json.dumps(record, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("web_cache: failed to write %s: %s", url, exc)
