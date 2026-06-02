"""Status bar widget showing model, MCP count, and connection status."""

from textual.widgets import Static


class StatusBar(Static):
    """Top bar showing model info and MCP server count."""

    DEFAULT_CSS = """
    StatusBar {
        dock: top;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self) -> None:
        super().__init__("mtv-agent  |  connecting...")

    def update_status(
        self,
        model: str,
        servers: int,
        tools: int,
        namespace: str | None = None,
    ) -> None:
        ns = f"  |  ns: {namespace}" if namespace else ""
        self.update(
            f"mtv-agent  |  model: {model}  |  MCP: {servers} servers, {tools} tools{ns}"
        )
