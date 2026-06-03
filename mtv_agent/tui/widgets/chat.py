"""Chat message display widgets."""

from textual.containers import VerticalScroll
from textual.widgets import Markdown, Static

from mtv_agent.tui.widgets.collapsible_block import CollapsibleBlock

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


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


class ThinkingIndicator(CollapsibleBlock):
    """Collapsible thinking log -- shows last 5 tool lines + spinner.

    Tool cards mounted via ``mount_tool_card`` live inside the collapsible
    contents, so they hide/show together with the thinking block.
    """

    DEFAULT_CSS = """
    ThinkingIndicator {
        color: $text-disabled;
        text-style: dim;
    }
    ThinkingIndicator > .collapsible--contents ToolCard {
        margin: 0 0 0 2;
    }
    """

    def __init__(self) -> None:
        self._tool_count = 0
        self._base_title = f"{SPINNER_FRAMES[0]} thinking..."
        super().__init__(title=self._base_title)
        self._frame = 0
        self._timer = None
        self._finished = False

    def on_mount(self) -> None:
        super().on_mount()
        self._timer = self.set_interval(0.15, self._tick)

    def watch_collapsed(self, collapsed: bool) -> None:
        super().watch_collapsed(collapsed)
        if not hasattr(self, "_finished"):
            return
        if collapsed:
            if self._timer is not None:
                self._timer.stop()
                self._timer = None
            self.set_title(f"thinking... ({self._tool_count} tool calls)")
        elif not self._finished:
            if self._timer is None:
                self._timer = self.set_interval(0.15, self._tick)

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % len(SPINNER_FRAMES)
        self._base_title = f"{SPINNER_FRAMES[self._frame]} thinking..."
        self.set_title(self._base_title)

    def add_tool_line(self, text: str) -> None:
        """Track tool call count."""
        self._tool_count += 1

    def mount_tool_card(self, card) -> None:
        """Mount a ToolCard inside the collapsible Contents container."""
        contents = self.query_one(self.Contents)
        contents.mount(card)

    def finish(self) -> None:
        """Collapse and stop the spinner when the answer arrives."""
        self._finished = True
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        self.set_title(f"thinking... ({self._tool_count} tool calls)")
        self.collapsed = True


class ChatArea(VerticalScroll):
    """Scrollable container for chat messages."""

    DEFAULT_CSS = """
    ChatArea {
        height: 1fr;
        padding: 0 1;
    }
    """
