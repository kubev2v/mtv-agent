"""Inline option selector with arrow-key navigation."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option


class OptionSelector(Vertical):
    """Shows a title and a list of selectable options."""

    DEFAULT_CSS = """
    OptionSelector {
        margin: 1 0 1 2;
        padding: 0 1;
        height: auto;
        max-height: 20;
    }
    OptionSelector .selector-title {
        color: $text;
        text-style: bold;
        margin: 0 0 0 0;
    }
    OptionSelector OptionList {
        height: auto;
        max-height: 16;
        margin: 0;
        background: $surface;
        color: $text;
    }
    """

    class Selected(Message):
        """Fired when the user picks an option."""

        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def __init__(
        self,
        title: str,
        options: list[str],
        current: str | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._options = options
        self._current = current

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="selector-title")
        items = []
        for opt in self._options:
            marker = " * " if opt == self._current else "   "
            items.append(Option(f"{marker}{opt}", id=opt))
        yield OptionList(*items, id="selector-options")

    def on_mount(self) -> None:
        ol = self.query_one("#selector-options", OptionList)
        ol.focus()
        if self._current and self._current in self._options:
            idx = self._options.index(self._current)
            ol.highlighted = idx

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.post_message(self.Selected(value=event.option.id))
