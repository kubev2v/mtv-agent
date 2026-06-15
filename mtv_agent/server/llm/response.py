"""LLM response validation helpers."""

from __future__ import annotations

from openai.types.chat import ChatCompletion


class EmptyResponseError(Exception):
    """Raised when the LLM returns no choices."""

    pass


class ContentFilteredError(Exception):
    """Raised when the response was blocked by a content filter."""

    pass


class TruncatedResponseError(Exception):
    """Raised when the response was truncated (context window exceeded)."""

    pass


def validate_response(response: ChatCompletion) -> None:
    """Check a ChatCompletion for known failure modes.

    Raises a descriptive exception instead of letting the caller hit
    an opaque IndexError or silently use a bad response.
    """
    if not response.choices:
        raise EmptyResponseError(
            "LLM returned an empty response -- it may be overloaded or misconfigured"
        )

    choice = response.choices[0]
    finish = choice.finish_reason

    if finish == "content_filter":
        raise ContentFilteredError(
            "Response blocked by content filter -- try rephrasing your request"
        )
    if finish == "length":
        raise TruncatedResponseError(
            "Response truncated -- the conversation exceeded the model's context window"
        )

    # Detect failed tool-call parsing: the model tried to call a tool but the
    # serving backend dropped it, returning empty tool_calls with no content.
    msg = choice.message
    has_content = bool(msg.content and msg.content.strip())
    has_tools = bool(msg.tool_calls)
    if not has_content and not has_tools:
        raise EmptyResponseError(
            "LLM returned an empty response -- the model may have failed to "
            "generate a valid tool call (check server logs for parsing errors)"
        )
