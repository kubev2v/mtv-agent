"""Tool-call execution with policy enforcement.

Handles the three policy outcomes for each tool call:
- reject: blocked unconditionally by server policy
- ask:    requires user approval before execution
- allow:  executed immediately (default)
"""

from __future__ import annotations

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


def trim_history(history: list[dict], max_chars: int = 80_000) -> list[dict]:
    """Keep only recent history that fits within a character budget."""
    total = 0
    result: list[dict] = []
    for msg in reversed(history):
        size = len(msg.get("content", ""))
        if total + size > max_chars:
            break
        result.append(msg)
        total += size
    result.reverse()
    return result


def _truncate(text: str, limit: int = 80_000) -> str:
    """Cap tool output to avoid blowing up the LLM context window."""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... (truncated)"
