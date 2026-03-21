"""Built-in web_fetch tool -- fetches a URL and returns Markdown."""

import logging
from pathlib import Path
from urllib.parse import urldefrag

from mtv_agent.lib.text_utils import DEFAULT_TRUNCATE_LIMIT, truncate
from mtv_agent.lib.tools.web.html_to_md import fetch_and_convert
from mtv_agent.lib.tools.web.md_sections import extract_section
from mtv_agent.lib.tools.web.web_cache import WebCache

logger = logging.getLogger(__name__)

TOOL_NAME = "web_fetch"

TRUNCATE_HINT = "Use a #fragment in the URL to fetch only a specific section."

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": (
            "Fetch a URL and return its content as Markdown. "
            "Use a #fragment to extract a single section by heading."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": (
                        "URL to fetch (may include #fragment for a specific section)."
                    ),
                },
            },
            "required": ["url"],
        },
    },
}


async def run(url: str, cache_dir: str | Path | None = None) -> str:
    """Fetch *url*, convert to Markdown, and optionally extract a section.

    When *cache_dir* is provided, results are cached on disk so that
    repeated fetches of the same URL skip the network round-trip.
    The full page is cached; fragment extraction runs after retrieval.
    """
    base_url, fragment = urldefrag(url)
    logger.info("web_fetch: %s (fragment=%r)", base_url, fragment or None)

    cache = WebCache(cache_dir) if cache_dir else None
    md: str | None = None

    if cache:
        md = cache.get(base_url)

    if md is None:
        try:
            md = await fetch_and_convert(base_url)
        except Exception as exc:
            logger.debug("web_fetch failed for %s", base_url, exc_info=True)
            return f"[error] {exc}"
        if cache:
            cache.put(base_url, md)

    if fragment:
        md = extract_section(md, fragment)

    return truncate(md, DEFAULT_TRUNCATE_LIMIT, TRUNCATE_HINT)
