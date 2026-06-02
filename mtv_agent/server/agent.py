"""Core agent loop -- simplified async generator."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator, Callable, Awaitable
from typing import Any

from mtv_agent.server.llm.client import LLMClient
from mtv_agent.server.mcp.manager import MCPManager

logger = logging.getLogger(__name__)

ApproveFunc = Callable[[str, dict], Awaitable[tuple[bool, str | None]]]


async def run_stream(
    message: str,
    llm: LLMClient,
    mcp: MCPManager,
    system_prompt: str,
    approve_fn: ApproveFunc | None = None,
    history: list[dict] | None = None,
    namespace: str | None = None,
    command: str | None = None,
    max_iterations: int = 20,
) -> AsyncGenerator[dict[str, Any], None]:
    """Run the agent loop, yielding SSE-ready event dicts.

    Iterates until the LLM produces a text response or hits *max_iterations*.
    """
    tools = mcp.get_tool_definitions()

    tools_with_flags = {
        td["function"]["name"]
        for td in tools
        if "flags" in td.get("function", {}).get("parameters", {}).get("properties", {})
    }

    trimmed_history = _trim_history(history or [])
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
    ]
    if command:
        messages.append(
            {"role": "system", "content": f"Follow this command:\n\n{command}"}
        )
    messages.extend([*trimmed_history, {"role": "user", "content": message}])

    for iteration in range(max_iterations):
        logger.debug("Agent iteration %d", iteration + 1)
        yield {"event": "thinking"}

        try:
            response = await llm.chat(messages, tools or None)
        except Exception as exc:
            logger.exception("LLM call failed")
            yield {"event": "error", "message": str(exc)}
            return

        choice = response.choices[0]

        if not choice.message.tool_calls:
            yield {
                "event": "content",
                "content": choice.message.content or "",
            }
            return

        messages.append(choice.message.model_dump())

        for tc in choice.message.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            if namespace and name in tools_with_flags:
                flags = args.setdefault("flags", {})
                if "namespace" not in flags:
                    flags["namespace"] = namespace

            policy = mcp.check_policy(name, args)

            if policy == "reject":
                result = "Tool call rejected by policy."
                yield {
                    "event": "tool_call",
                    "name": name,
                    "arguments": args,
                    "pending": False,
                }
                yield {
                    "event": "tool_rejected",
                    "name": name,
                    "reason": "blocked by policy",
                }
            elif policy == "ask" and approve_fn:
                yield {
                    "event": "tool_call",
                    "name": name,
                    "arguments": args,
                    "pending": True,
                }
                approved, reason = await approve_fn(name, args)
                if not approved:
                    result = f"Tool call denied by user. {reason or ''}"
                    yield {
                        "event": "tool_rejected",
                        "name": name,
                        "reason": reason or "denied",
                    }
                else:
                    try:
                        result = await mcp.call_tool(name, args)
                    except Exception as exc:
                        logger.exception("Tool call %s failed", name)
                        result = f"Error executing tool: {exc}"
                    yield {
                        "event": "tool_result",
                        "name": name,
                        "result": _truncate(result),
                    }
            else:
                yield {
                    "event": "tool_call",
                    "name": name,
                    "arguments": args,
                    "pending": False,
                }
                try:
                    result = await mcp.call_tool(name, args)
                except Exception as exc:
                    logger.exception("Tool call %s failed", name)
                    result = f"Error executing tool: {exc}"
                yield {
                    "event": "tool_result",
                    "name": name,
                    "result": _truncate(result),
                }

            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    yield {"event": "error", "message": "Max iterations reached"}


MAX_HISTORY_CHARS = 80_000


def _trim_history(history: list[dict]) -> list[dict]:
    """Keep only recent history that fits within a character budget."""
    total = 0
    result: list[dict] = []
    for msg in reversed(history):
        size = len(msg.get("content", ""))
        if total + size > MAX_HISTORY_CHARS:
            break
        result.append(msg)
        total += size
    result.reverse()
    return result


def _truncate(text: str, limit: int = 80_000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... (truncated)"
