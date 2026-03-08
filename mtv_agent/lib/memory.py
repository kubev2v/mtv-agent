"""In-memory conversation history, keyed by session ID."""

import time


def _trim_to_last_n_turns(messages: list[dict], max_turns: int) -> list[dict]:
    """Keep only the last *max_turns* turns.

    A turn starts at each ``role == "user"`` message and includes every
    subsequent message until the next user message (tool calls, tool
    results, assistant replies, etc.).
    """
    boundaries: list[int] = [
        i for i, m in enumerate(messages) if m.get("role") == "user"
    ]
    if len(boundaries) <= max_turns:
        return messages
    cut = boundaries[-max_turns]
    return messages[cut:]


class ChatMemory:
    """Stores the full message sequence (including tool calls) per session.

    Parameters:
        max_turns:   Maximum conversation turns kept per session.
        ttl_seconds: Seconds of inactivity before a session is evicted.
    """

    def __init__(self, max_turns: int = 20, ttl_seconds: int = 3600) -> None:
        self.max_turns = max_turns
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, list[dict]] = {}
        self._last_access: dict[str, float] = {}

    def load(self, session_id: str) -> list[dict]:
        """Return the stored messages for *session_id* (may be empty)."""
        self._evict_stale()
        self._last_access[session_id] = time.monotonic()
        return list(self._sessions.get(session_id, []))

    def append(self, session_id: str, turn_messages: list[dict]) -> None:
        """Record one full conversation turn.

        *turn_messages* should contain the complete OpenAI-format sequence
        for the turn: user message, assistant messages (with tool_calls),
        tool-result messages, and the final assistant reply.
        """
        history = self._sessions.setdefault(session_id, [])
        history.extend(turn_messages)
        self._sessions[session_id] = _trim_to_last_n_turns(history, self.max_turns)
        self._last_access[session_id] = time.monotonic()

    def _evict_stale(self) -> None:
        """Remove sessions that have been idle longer than *ttl_seconds*."""
        cutoff = time.monotonic() - self.ttl_seconds
        stale = [sid for sid, ts in self._last_access.items() if ts < cutoff]
        for sid in stale:
            self._sessions.pop(sid, None)
            self._last_access.pop(sid, None)
