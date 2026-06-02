"""Chat message display widgets."""

from textual.containers import VerticalScroll
from textual.widgets import Collapsible, Markdown, Static

from mtv_agent.tui.widgets.collapse_header import CollapseHeader

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

MAX_VISIBLE_LINES = 5


class UserMessage(Static):
    """Displays a user message."""

    DEFAULT_CSS = """
    UserMessage {
        margin: 1 0 0 2;
        padding: 0 1;
        color: $text;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__(f"[bold cyan]You:[/] {text}")


class ErrorMessage(Static):
    """Displays an error with a distinctive red border."""

    DEFAULT_CSS = """
    ErrorMessage {
        margin: 1 0 0 2;
        padding: 0 1;
        border-left: thick $error;
        color: $error;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__(f"[bold]Error:[/] {text}")


class AssistantMessage(Markdown):
    """Displays an assistant message as rendered Markdown."""

    DEFAULT_CSS = """
    AssistantMessage {
        margin: 1 0 0 2;
        padding: 0 1;
    }
    """

    def __init__(self, content: str) -> None:
        super().__init__(content)


class ThinkingIndicator(Collapsible):
    """Collapsible thinking log -- shows last 5 tool lines + spinner.

    Tool cards mounted via ``mount_tool_card`` live inside the collapsible
    contents, so they hide/show together with the thinking block.
    """

    DEFAULT_CSS = """
    ThinkingIndicator {
        margin: 1 0 0 0;
        padding: 0;
        color: $text-disabled;
        text-style: dim;
        border-top: solid grey;
    }
    ThinkingIndicator > CollapsibleTitle {
        display: none;
    }
    ThinkingIndicator ToolCard {
        margin: 0 0 0 2;
    }
    """

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._log = Static("", classes="thinking-log")
        self._log.display = False
        self._base_title = f"{SPINNER_FRAMES[0]} thinking..."
        super().__init__(
            self._log,
            title=self._base_title,
            collapsed=False,
            collapsed_symbol="",
            expanded_symbol="",
        )
        self._frame = 0
        self._timer = None
        self._header = CollapseHeader(self._base_title, collapsed=False)

    def compose(self):
        yield self._header
        yield from super().compose()

    def watch_collapsed(self, collapsed: bool) -> None:
        if hasattr(self, "_header"):
            self._header.set_collapsed(collapsed)

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.15, self._tick)

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(SPINNER_FRAMES)
        self._base_title = f"{SPINNER_FRAMES[self._frame]} thinking..."
        self._header.set_title(self._base_title)

    def add_tool_line(self, text: str) -> None:
        """Append a tool-call line to the log."""
        self._lines.append(text)
        visible = self._lines[-MAX_VISIBLE_LINES:]
        self._log.update("\n".join(visible))
        self._log.display = True

    def mount_tool_card(self, card) -> None:
        """Mount a ToolCard inside the collapsible Contents container."""
        contents = self.query_one(self.Contents)
        contents.mount(card)

    def finish(self) -> None:
        """Collapse and stop the spinner when the answer arrives."""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        self._base_title = f"thinking... ({len(self._lines)} tool calls)"
        self._header.set_title(self._base_title)
        self.collapsed = True


class ChatArea(VerticalScroll):
    """Scrollable container for chat messages."""

    DEFAULT_CSS = """
    ChatArea {
        height: 1fr;
        padding: 0 1;
    }
    """
