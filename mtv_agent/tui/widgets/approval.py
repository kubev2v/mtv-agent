"""Inline approval prompt with arrow-key selection."""

import json

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option


class ApprovalPrompt(Vertical):
    """Shows tool call details and approve/reject options."""

    DEFAULT_CSS = """
    ApprovalPrompt {
        margin: 0 0 0 4;
        padding: 0 1;
        height: auto;
        max-height: 18;
        background: $surface;
        border: solid grey;
    }
    ApprovalPrompt .approval-header {
        color: $warning;
        text-style: bold;
        margin: 0 0 0 0;
    }
    ApprovalPrompt .approval-detail {
        color: $text-muted;
        text-style: dim;
        margin: 0 0 0 2;
    }
    ApprovalPrompt OptionList {
        height: 6;
        margin: 1 0 0 0;
        background: $surface;
        color: $text;
    }
    """

    class Responded(Message):
        """Fired when the user picks an approval option."""

        def __init__(self, approved: bool, always: bool = False) -> None:
            super().__init__()
            self.approved = approved
            self.always = always

    def __init__(self, name: str, arguments: dict | None = None) -> None:
        super().__init__()
        self._name = name
        self._arguments = arguments or {}

    def compose(self) -> ComposeResult:
        yield Static(
            f"Tool '{self._name}' requires approval:",
            classes="approval-header",
        )
        args_display = json.dumps(self._arguments, indent=2)
        if len(args_display) > 300:
            args_display = args_display[:300] + "\n..."
        yield Static(args_display, classes="approval-detail")
        yield OptionList(
            Option("  Approve        -- allow this call", id="approve"),
            Option("  Reject         -- deny this call", id="reject"),
            Option("  Always Accept  -- auto-approve this tool", id="always-accept"),
            Option("  Always Reject  -- auto-reject this tool", id="always-reject"),
            id="approval-options",
        )

    def on_mount(self) -> None:
        ol = self.query_one("#approval-options", OptionList)
        ol.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        oid = event.option.id
        if oid == "approve":
            self.post_message(self.Responded(approved=True))
        elif oid == "reject":
            self.post_message(self.Responded(approved=False))
        elif oid == "always-accept":
            self.post_message(self.Responded(approved=True, always=True))
        elif oid == "always-reject":
            self.post_message(self.Responded(approved=False, always=True))
