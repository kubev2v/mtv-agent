"""Collapsible tool call display -- muted style, collapsed after result."""

from textual.widgets import Collapsible, Static

from mtv_agent.tui.widgets.collapse_header import CollapseHeader


class ToolCard(Collapsible):
    """Shows a tool call as a collapsible block with muted styling."""

    DEFAULT_CSS = """
    ToolCard {
        margin: 0 0 0 0;
        padding: 0;
        border-top: none;
        color: $text-muted;
        text-style: dim;
    }
    ToolCard > CollapsibleTitle {
        display: none;
    }
    """

    def __init__(
        self,
        name: str,
        arguments: dict | None = None,
        pending: bool = False,
    ) -> None:
        args_str = ""
        if arguments:
            args_str = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
            if len(args_str) > 120:
                args_str = args_str[:120] + "..."
        status = " -- awaiting approval" if pending else ""
        self._base_title = f"[tool] {name}({args_str}){status}"
        self._result_widget = Static("", classes="tool-result")
        super().__init__(
            self._result_widget,
            title=self._base_title,
            collapsed=False,
            collapsed_symbol="",
            expanded_symbol="",
        )
        self._name = name
        self._header = CollapseHeader(
            self._base_title,
            collapsed=False,
            arrow_down="▽",
            arrow_right="▷",
        )

    def compose(self):
        yield self._header
        yield from super().compose()

    def watch_collapsed(self, collapsed: bool) -> None:
        if hasattr(self, "_header"):
            self._header.set_collapsed(collapsed)

    def set_result(self, result: str) -> None:
        if len(result) > 2000:
            result = result[:2000] + "\n... (truncated in display)"
        self._result_widget.update(result)
        self._base_title = self._base_title.replace(" -- awaiting approval", "")
        self._header.set_title(self._base_title)
        self.collapsed = True

    def set_approved(self, label: str = "Approved") -> None:
        self._base_title = self._base_title.replace(" -- awaiting approval", "")
        self._header.set_title(f"{self._base_title} -- {label}")
        self._result_widget.update(label)

    def set_rejected(self, reason: str) -> None:
        self._result_widget.update(f"Rejected: {reason}")
        self._base_title = self._base_title.replace(
            " -- awaiting approval", " [rejected]"
        )
        self._header.set_title(self._base_title)
        self.collapsed = True
