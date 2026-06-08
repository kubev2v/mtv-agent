"""Tool-call execution with policy enforcement.

Handles the three policy outcomes for each tool call:
- reject: blocked unconditionally by server policy
- ask:    requires user approval before execution
- allow:  executed immediately (default)
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator, Callable, Awaitable
from typing import Any

from mtv_agent.server.mcp.manager import MCPManager

logger = logging.getLogger(__name__)

ApproveFunc = Callable[[str, dict], Awaitable[tuple[bool, str | None]]]


async def execute_tool_call(
    name: str,
    args: dict,
    mcp: MCPManager,
    approve_fn: ApproveFunc | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Execute a single tool call, yielding SSE events and the final result.

    The last yielded dict always has key ``"_result"`` containing the raw
    string to feed back to the LLM as the tool response.
    """
    policy = mcp.check_policy(name, args)

    if policy == "reject":
        yield {"event": "tool_call", "name": name, "arguments": args, "pending": False}
        yield {"event": "tool_rejected", "name": name, "reason": "blocked by policy"}
        yield {"_result": "Tool call rejected by policy."}
        return

    # "ask" policy -- wait for user approval before running the tool
    if policy == "ask" and approve_fn:
        yield {"event": "tool_call", "name": name, "arguments": args, "pending": True}
        approved, reason = await approve_fn(name, args)
        if not approved:
            yield {"event": "tool_rejected", "name": name, "reason": reason or "denied"}
            yield {"_result": f"Tool call denied by user. {reason or ''}"}
            return

    # "allow" policy (or approved "ask") -- execute the tool
    else:
        yield {"event": "tool_call", "name": name, "arguments": args, "pending": False}

    result = await _safe_call(mcp, name, args)
    yield {"event": "tool_result", "name": name, "result": _truncate(result)}
    yield {"_result": result}


async def _safe_call(mcp: MCPManager, name: str, args: dict) -> str:
    try:
        return await mcp.call_tool(name, args)
    except Exception as exc:
        logger.exception("Tool call %s failed", name)
        return f"Error executing tool: {exc}"


def trim_history(history: list[dict], max_chars: int = 160_000) -> list[dict]:
    """Keep only recent history that fits within a character budget.

    Messages are grouped so that an assistant message with ``tool_calls`` and
    its subsequent ``tool`` messages are treated as an atomic unit -- they are
    never split, preventing OpenAI API errors.
    """
    groups = _group_messages(history)
    total = 0
    kept: list[list[dict]] = []
    for group in reversed(groups):
        size = _group_size(group)
        if total + size > max_chars:
            break
        kept.append(group)
        total += size
    kept.reverse()
    return [msg for group in kept for msg in group]


def _group_messages(messages: list[dict]) -> list[list[dict]]:
    """Group messages into atomic units for trimming.

    A tool-call turn (assistant with ``tool_calls`` + following ``tool``
    messages) is kept as one group.  Everything else is its own group.
    """
    groups: list[list[dict]] = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            group = [msg]
            i += 1
            while i < len(messages) and messages[i].get("role") == "tool":
                group.append(messages[i])
                i += 1
            groups.append(group)
        else:
            groups.append([msg])
            i += 1
    return groups


def _group_size(group: list[dict]) -> int:
    """Estimate the character size of a message group."""
    total = 0
    for msg in group:
        total += len(msg.get("content") or "")
        if msg.get("tool_calls"):
            total += len(json.dumps(msg["tool_calls"]))
    return total


def _truncate(text: str, limit: int = 160_000) -> str:
    """Cap tool output to avoid blowing up the LLM context window."""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... (truncated)"
