"""Built-in web_fetch tool -- fetches a URL and returns Markdown."""

import logging
from urllib.parse import urldefrag

from mtv_agent.lib.html_to_md import fetch_and_convert
from mtv_agent.lib.md_sections import extract_section
from mtv_agent.lib.text_utils import DEFAULT_TRUNCATE_LIMIT, truncate

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


async def run(url: str) -> str:
    """Fetch *url*, convert to Markdown, and optionally extract a section."""
    base_url, fragment = urldefrag(url)
    logger.info("web_fetch: %s (fragment=%r)", base_url, fragment or None)

    try:
        md = await fetch_and_convert(base_url)
    except Exception as exc:
        return f"[error] {exc}"

    if fragment:
        md = extract_section(md, fragment)

    return truncate(md, DEFAULT_TRUNCATE_LIMIT, TRUNCATE_HINT)
