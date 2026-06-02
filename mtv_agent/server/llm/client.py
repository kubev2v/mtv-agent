"""Thin async wrapper around an OpenAI-compatible LLM server."""

from __future__ import annotations

import logging

import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 360


class LLMClient:
    """Sends chat-completion requests to any OpenAI-compatible endpoint."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.model = model
        self._client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=httpx.Timeout(timeout, connect=10.0),
        )

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> ChatCompletion:
        kwargs: dict = dict(model=self.model, messages=messages)
        if tools:
            kwargs["tools"] = tools
        return await self._client.chat.completions.create(**kwargs)


async def discover_model(base_url: str, api_key: str) -> str:
    """Query /v1/models and return the first available model ID."""
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    models = await client.models.list()
    if not models.data:
        raise RuntimeError(f"No models found at {base_url}")
    return models.data[0].id
