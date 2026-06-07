"""Chat input bar widget."""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import Key
from textual.message import Message
from textual.suggester import SuggestFromList
from textual.widgets import Input

from mtv_agent.tui.clipboard import read_system_clipboard

SLASH_COMMANDS = [
    "/help",
    "/ns ",
    "/ns --all",
    "/clear",
    "/id",
    "/resume ",
    "/status",
    "/history",
    "/policy",
    "/policy reset",
    "/quit",
    "/exit",
    "exit",
    "quit",
]

MAX_HISTORY = 100


class _ClipboardInput(Input):
    """Input subclass that falls back to the system clipboard on paste."""

    BINDINGS = [
        Binding("ctrl+v,super+v", "paste", "Paste", show=False),
    ]

    def action_paste(self) -> None:
        text = self.app.clipboard or read_system_clipboard()
        if text:
            line = text.splitlines()[0]
            start, end = self.selection
            self.replace(line, start, end)


class ChatInput(Horizontal):
    """Input bar with slash-command autocomplete and prompt history."""

    DEFAULT_CSS = """
    ChatInput {
        dock: bottom;
        height: auto;
        padding: 0 1;
        background: $surface;
    }
    ChatInput Input {
        width: 1fr;
        border-top: solid grey;
        border-bottom: solid grey;
        border-left: none;
        border-right: none;
    }
    ChatInput Input:focus {
        border-top: solid grey;
        border-bottom: solid grey;
        border-left: none;
        border-right: none;
    }
    """

    class Submitted(Message):
        """Fired when the user submits a message."""

        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def __init__(self) -> None:
        super().__init__()
        self._input_history: list[str] = []
        self._history_index: int = -1
        self._saved_input: str = ""
        self._all_commands: list[str] = list(SLASH_COMMANDS)

    def compose(self) -> ComposeResult:
        yield _ClipboardInput(
            placeholder="Type a message or / for commands...",
            id="chat-input",
            suggester=SuggestFromList(self._all_commands, case_sensitive=False),
        )

    def update_suggestions(self, extra_commands: list[str]) -> None:
        """Add dynamic commands (e.g. playbooks) to the autocomplete list."""
        for cmd in extra_commands:
            if cmd not in self._all_commands:
                self._all_commands.append(cmd)
        inp = self.query_one("#chat-input", Input)
        inp.suggester = SuggestFromList(self._all_commands, case_sensitive=False)

    @on(Input.Submitted, "#chat-input")
    def on_submit(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value:
            event.input.clear()
            if not self._input_history or self._input_history[-1] != value:
                self._input_history.append(value)
                if len(self._input_history) > MAX_HISTORY:
                    self._input_history.pop(0)
            self._history_index = -1
            self._saved_input = ""
            self.post_message(self.Submitted(value))

    def on_key(self, event: Key) -> None:
        inp = self.query_one("#chat-input", Input)
        if not inp.has_focus:
            return

        if event.key == "up":
            event.prevent_default()
            if not self._input_history:
                return
            if self._history_index == -1:
                self._saved_input = inp.value
                self._history_index = len(self._input_history) - 1
            elif self._history_index > 0:
                self._history_index -= 1
            inp.value = self._input_history[self._history_index]
            inp.cursor_position = len(inp.value)

        elif event.key == "down":
            event.prevent_default()
            if self._history_index == -1:
                return
            if self._history_index < len(self._input_history) - 1:
                self._history_index += 1
                inp.value = self._input_history[self._history_index]
            else:
                self._history_index = -1
                inp.value = self._saved_input
            inp.cursor_position = len(inp.value)
