"""Fetch a URL and convert its HTML body to Markdown."""

import json
import re

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

TIMEOUT = 30
USER_AGENT = "mtv-agent/0.1 (web_fetch tool)"

_STRIP_TAGS = frozenset(
    {
        "script",
        "style",
        "nav",
        "footer",
        "aside",
        "svg",
        "noscript",
        "iframe",
        "form",
        "button",
    }
)
_STRIP_ROLES = frozenset(
    {
        "navigation",
        "banner",
        "contentinfo",
        "complementary",
        "search",
    }
)

_BLANK_LINES_RE = re.compile(r"\n{3,}")
_FENCED_OR_PRE_RE = re.compile(r"(```.*?```|<pre[\s>].*?</pre>)", re.DOTALL)


def _clean_html(html: str) -> str:
    """Extract main content and strip non-content elements.

    Uses only standard HTML5 landmark elements and ARIA roles --
    no site-specific class names or heuristics.
    """
    soup = BeautifulSoup(html, "html.parser")

    main = (
        soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"})
    )
    if main:
        soup = BeautifulSoup(str(main), "html.parser")

    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    for tag in soup.find_all(attrs={"role": lambda v: v and v in _STRIP_ROLES}):
        tag.decompose()

    for tag in soup.find_all(True):
        if tag.has_attr("style"):
            del tag["style"]

    return str(soup)


def _postprocess_markdown(md: str) -> str:
    """Collapse excessive blank lines outside fenced code blocks and <pre> sections."""
    parts = _FENCED_OR_PRE_RE.split(md)
    for i, part in enumerate(parts):
        if not _FENCED_OR_PRE_RE.fullmatch(part):
            parts[i] = _BLANK_LINES_RE.sub("\n\n", part)
    return "".join(parts).strip()


async def fetch_and_convert(url: str) -> str:
    """GET *url* and return the response body as Markdown.

    Content-Type handling:
    - ``text/plain`` or ``text/markdown`` -- returned as-is.
    - ``application/json`` -- pretty-printed inside a code block.
    - Everything else -- HTML is cleaned with BeautifulSoup then
      converted to Markdown via ``markdownify``.
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
        resp = await client.get(url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")
    body = resp.text

    if "text/plain" in content_type or "text/markdown" in content_type:
        return body

    media_type = content_type.split(";")[0].strip()
    if "application/json" in content_type or media_type.endswith("+json"):
        try:
            formatted = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            formatted = body
        return f"```json\n{formatted}\n```"

    cleaned = _clean_html(body)
    md = markdownify(cleaned, heading_style="ATX", strip=["script", "style"])
    return _postprocess_markdown(md)
