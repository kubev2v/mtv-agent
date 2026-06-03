"""Core agent loop -- simplified async generator."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from mtv_agent.server.llm.client import LLMClient
from mtv_agent.server.mcp.manager import MCPManager
from mtv_agent.server.tools import ApproveFunc, execute_tool_call, trim_history

logger = logging.getLogger(__name__)


async def run_stream(
    message: str,
    llm: LLMClient,
    mcp: MCPManager,
    system_prompt: str,
    approve_fn: ApproveFunc | None = None,
    history: list[dict] | None = None,
    namespace: str | None = None,
    command: str | None = None,
    session_id: str | None = None,
    max_iterations: int = 20,
    max_history_chars: int = 80_000,
) -> AsyncGenerator[dict[str, Any], None]:
    """Run the agent loop, yielding SSE-ready event dicts.

    Iterates until the LLM produces a text response or hits *max_iterations*.

    **Initial message setup** (built by ``_build_messages``):

    1. System prompt -- always first, sets the agent persona and instructions.
    2. History -- previous user/assistant turns from the chat session, trimmed
       from the oldest end to stay within *max_history_chars* so we don't
       exceed the LLM context window.
    3. User message -- the current request. When the user invokes a
       slash-command (e.g. ``/check-cluster-health``), its body replaces the
       plain user message, with the original input appended for context.

    **Iteration loop** (each pass through the ``for`` loop):

    - Send the messages + tool definitions to the LLM.
    - If the LLM responds with plain text (no tool calls), yield it and stop.
    - If the LLM requests tool calls, append its response (via ``model_dump()``)
      to the messages list, then execute each tool and append the result.
      The OpenAI API requires this pairing: an assistant message with
      ``tool_calls`` followed by a ``tool`` message for each call.
    - The loop then repeats, giving the LLM the tool results so it can
      decide to call more tools or produce a final text answer.

    Example messages list after one tool-call iteration::

        [
          {"role": "system",    "content": "<system prompt>"},
          {"role": "user",      "content": "<history msg 1>"},
          {"role": "assistant", "content": "<history msg 2>"},
          {"role": "user",      "content": "<user message or command + user message>"},
          {"role": "assistant", "tool_calls": [{"id": "...", ...}]},
          {"role": "tool",      "tool_call_id": "...", "content": "<result>"},
        ]
    """
    tools = mcp.get_tool_definitions()

    messages = _build_messages(
        system_prompt, command, history, message, max_history_chars
    )

    if llm.dumper and session_id:
        llm.dumper.set_session(session_id)

    for iteration in range(max_iterations):
        logger.debug("Agent iteration %d", iteration + 1)
        yield {"event": "thinking"}

        if llm.dumper:
            llm.dumper.next_iteration()

        try:
            response = await llm.chat(messages, tools or None)
        except Exception as exc:
            logger.exception("LLM call failed")
            yield {"event": "error", "message": str(exc)}
            return

        choice = response.choices[0]

        if not choice.message.tool_calls:
            yield {"event": "content", "content": choice.message.content or ""}
            return

        messages.append(choice.message.model_dump())

        for tc in choice.message.tool_calls:
            name = tc.function.name
            args = _parse_args(tc)
            if namespace:
                args.setdefault("flags", {}).setdefault("namespace", namespace)

            result = ""
            async for event in execute_tool_call(name, args, mcp, approve_fn):
                if "_result" in event:
                    result = event["_result"]
                else:
                    yield event

            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    yield {"event": "error", "message": "Max iterations reached"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_messages(
    system_prompt: str,
    command: str | None,
    history: list[dict] | None,
    user_message: str,
    max_history_chars: int = 80_000,
) -> list[dict]:
    """Assemble the initial message list for the LLM."""
    msgs: list[dict] = [{"role": "system", "content": system_prompt}]
    msgs.extend(trim_history(history or [], max_history_chars))
    if command:
        msgs.append(
            {
                "role": "user",
                "content": f"Follow this command:\n\n{command}\n\nUser message: {user_message}",
            }
        )
    else:
        msgs.append({"role": "user", "content": user_message})
    return msgs


def _parse_args(tc: object) -> dict:
    """JSON-parse tool-call arguments with a safe fallback."""
    try:
        return json.loads(tc.function.arguments)
    except json.JSONDecodeError:
        return {}
