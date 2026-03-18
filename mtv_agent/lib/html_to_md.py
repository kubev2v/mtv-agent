"""Fetch a URL and convert its HTML body to Markdown."""

import httpx
from markdownify import markdownify

TIMEOUT = 30
USER_AGENT = "mtv-agent/0.1 (web_fetch tool)"


async def fetch_and_convert(url: str) -> str:
    """GET *url* and return the response body as Markdown.

    If the Content-Type is already ``text/plain`` or ``text/markdown``
    the body is returned as-is.  Otherwise HTML is converted to
    Markdown with ATX-style headings and ``<script>``/``<style>`` tags
    stripped.
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
        resp = await client.get(url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")
    body = resp.text

    if "text/plain" in content_type or "text/markdown" in content_type:
        return body

    return markdownify(body, heading_style="ATX", strip=["script", "style"])
