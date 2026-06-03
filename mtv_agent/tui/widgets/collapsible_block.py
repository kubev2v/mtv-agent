"""Shared base for collapsible blocks (thinking, info, etc.)."""

from textual.widgets import Collapsible
from textual.widgets._collapsible import CollapsibleTitle

from mtv_agent.tui.widgets.collapse_header import CollapseHeader


class CollapsibleBlock(Collapsible):
    """Base collapsible block with a custom CollapseHeader.

    Subclasses get:
    - Hidden default CollapsibleTitle (replaced by CollapseHeader)
    - Arrow toggle via CollapseHeader
    - Consistent margin (top and bottom)
    """

    DEFAULT_CSS = """
    .cb {
        margin: 1 0 1 0;
        padding: 0;
        border: none;
        background: transparent;
    }
    """

    def __init__(self, *children, title: str = "", collapsed: bool = False) -> None:
        self._header = CollapseHeader(title, collapsed=collapsed)
        super().__init__(
            *children,
            title=title,
            collapsed=collapsed,
            collapsed_symbol="",
            expanded_symbol="",
            classes="cb",
        )

    def compose(self):
        yield self._header
        yield from super().compose()

    def on_mount(self) -> None:
        try:
            self.query_one(CollapsibleTitle).display = False
        except Exception:
            pass

    def watch_collapsed(self, collapsed: bool) -> None:
        if hasattr(self, "_header"):
            self._header.set_collapsed(collapsed)

    def set_title(self, title: str) -> None:
        self._header.set_title(title)
