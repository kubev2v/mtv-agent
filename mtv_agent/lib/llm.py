"""Thin async wrapper around an OpenAI-compatible LLM server."""

import logging

import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)


DEFAULT_LLM_TIMEOUT = 120  # seconds


class LLMClient:
    """Sends chat-completion requests to any OpenAI-compatible endpoint."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = DEFAULT_LLM_TIMEOUT,
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
        """Send a chat completion request and return the raw response."""
        kwargs: dict = dict(model=self.model, messages=messages)
        if tools:
            kwargs["tools"] = tools
        return await self._client.chat.completions.create(**kwargs)

    async def list_models(self) -> list[str]:
        """Return the IDs of all models available on the server."""
        models = await self._client.models.list()
        return [m.id for m in models.data]


async def discover_model(base_url: str, api_key: str) -> str:
    """Query /v1/models and return the first available model ID."""
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    models = await client.models.list()
    if not models.data:
        raise RuntimeError(f"No models found at {base_url}")
    return models.data[0].id


async def discover_context_window(
    base_url: str, api_key: str, model_id: str
) -> int | None:
    """Try to get the context window from LM Studio's native API.

    Calls GET /api/v0/models/{model_id} which returns max_context_length.
    Returns None if the server doesn't support this endpoint.
    """
    # base_url is like "http://localhost:1234/v1" -- strip /v1 to get the root
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3]

    url = f"{root}/api/v0/models/{model_id}"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            ctx = data.get("max_context_length")
            if isinstance(ctx, int) and ctx > 0:
                return ctx
    except Exception as exc:
        logger.debug("Could not discover context window: %s", exc)
    return None
