"""Clickable header for Collapsible with a right-aligned arrow."""

from textual.containers import Horizontal
from textual.widgets import Static
from textual.widgets._collapsible import CollapsibleTitle


class CollapseHeader(Horizontal):
    """Horizontal bar: title (1fr) + arrow (auto), click toggles parent."""

    DEFAULT_CSS = """
    CollapseHeader {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }
    CollapseHeader .ch-title {
        width: 1fr;
    }
    CollapseHeader .ch-arrow {
        width: auto;
        min-width: 1;
    }
    """

    ARROW_DOWN = "▼"
    ARROW_RIGHT = "▶"

    def __init__(
        self,
        title: str = "",
        collapsed: bool = False,
        arrow_down: str | None = None,
        arrow_right: str | None = None,
    ) -> None:
        super().__init__()
        self._arrow_down = arrow_down or self.ARROW_DOWN
        self._arrow_right = arrow_right or self.ARROW_RIGHT
        arrow = self._arrow_right if collapsed else self._arrow_down
        self._title_widget = Static(title, classes="ch-title")
        self._arrow_widget = Static(arrow, classes="ch-arrow")

    def compose(self):
        yield self._title_widget
        yield self._arrow_widget

    def on_click(self) -> None:
        collapsible = self.parent
        if collapsible is not None:
            collapsible.collapsed = not collapsible.collapsed

    def set_title(self, title: str) -> None:
        self._title_widget.update(title)

    def set_collapsed(self, collapsed: bool) -> None:
        arrow = self._arrow_right if collapsed else self._arrow_down
        self._arrow_widget.update(arrow)

    @staticmethod
    def hide_default_title(collapsible) -> None:
        """Hide the built-in CollapsibleTitle so only our header shows."""
        try:
            collapsible.query_one(CollapsibleTitle).display = False
        except Exception:
            pass
