"""Textual TUI for mtv-agent -- connects to the server via HTTP/SSE."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Static

from mtv_agent.server.config import load_tui_theme, save_tui_theme
from mtv_agent.tui.client import AgentClient
from mtv_agent.tui.widgets.approval import ApprovalPrompt
from mtv_agent.tui.widgets.chat import (
    AssistantMessage,
    ChatArea,
    ErrorMessage,
    ThinkingIndicator,
    UserMessage,
)
from mtv_agent.tui.widgets.collapsible_block import CollapsibleBlock
from mtv_agent.tui.widgets.header import StatusBar
from mtv_agent.tui.widgets.input import ChatInput
from mtv_agent.tui.widgets.option_selector import OptionSelector
from mtv_agent.tui.widgets.tool_card import ToolCard

logger = logging.getLogger(__name__)


def _friendly_error(exc: Exception) -> str:
    """Turn raw exceptions into short, readable messages."""
    name = type(exc).__name__
    msg = str(exc)
    if "ConnectError" in name or "ConnectionRefused" in msg:
        return "Server is not running (start with: uv run mtv-server)"
    if "TimeoutException" in name or "timed out" in msg.lower():
        return "Request timed out -- the server may be overloaded"
    if "status_code" in msg or hasattr(exc, "response"):
        return f"Server returned an error ({msg})"
    if "RemoteProtocolError" in name or "Server disconnected" in msg:
        return "Server closed the connection -- check server logs for errors"
    if len(msg) > 120:
        msg = msg[:120] + "..."
    return f"Connection lost: {msg}" if msg else "Connection lost unexpectedly"


def _info_block(title: str, body: str) -> CollapsibleBlock:
    return CollapsibleBlock(Static(body), title=title)


class MTVApp(App):
    """Main TUI application."""

    TITLE = "mtv-agent"
    DEFAULT_CSS = """
    Screen { layout: vertical; }
    """
    BINDINGS = [
        ("ctrl+q,super+q", "quit", "Quit"),
        ("ctrl+l", "clear", "Clear"),
    ]

    def __init__(self, server_url: str = "http://localhost:8000"):
        super().__init__()
        self.theme = load_tui_theme()
        self.client = AgentClient(server_url)
        self.session_id: str | None = None
        self._namespace: str | None = None
        self._history: list[dict] = []
        self._thinking: ThinkingIndicator | None = None
        self._current_tool: ToolCard | None = None
        self._approval_event: asyncio.Event | None = None
        self._approval_result: bool = False
        self._approval_always: bool = False
        self._approval_tool_name: str = ""
        self._commands: dict[str, dict] = {}

    def compose(self) -> ComposeResult:
        yield StatusBar()
        yield ChatArea()
        yield ChatInput()

    async def on_mount(self) -> None:
        self._refresh_status()
        self._load_commands()
        self.query_one("#chat-input").focus()

    @work(exclusive=True, thread=False)
    async def _refresh_status(self) -> None:
        try:
            status = await self.client.get_status()
            bar = self.query_one(StatusBar)
            bar.update_status(
                model=status.get("model", "?"),
                servers=status.get("servers", 0),
                tools=status.get("tools", 0),
                namespace=self._namespace,
            )
        except Exception:
            bar = self.query_one(StatusBar)
            bar.update(
                "mtv-agent  |  Server unreachable -- start with: uv run mtv-server"
            )

    @work(exclusive=False, thread=False)
    async def _load_commands(self) -> None:
        try:
            cmd_list = await self.client.get_commands()
            for cmd in cmd_list:
                self._commands[cmd["name"]] = cmd
            chat_input = self.query_one(ChatInput)
            chat_input.update_suggestions([f"/{name} " for name in self._commands])
        except Exception as exc:
            logger.warning("Could not fetch commands: %s", exc)

    # -- message handling ----------------------------------------------------

    @on(ChatInput.Submitted)
    async def on_chat_submitted(self, event: ChatInput.Submitted) -> None:
        message = event.value

        if message.startswith("/"):
            self._handle_slash(message)
            return

        if message.strip().lower() in ("exit", "quit"):
            await self.client.close()
            self.exit()
            return

        area = self.query_one(ChatArea)
        area.mount(UserMessage(message))
        area.scroll_end(animate=False)
        self._stream_response(message)

    def _handle_slash(self, cmd: str) -> None:
        area = self.query_one(ChatArea)
        parts = cmd.strip().split()
        command = parts[0].lower()

        if command == "/clear":
            area.remove_children()
            self._history.clear()
            self.session_id = None
            self._namespace = None
            self._update_title()
            self._refresh_status()
        elif command == "/ns":
            if len(parts) < 2:
                self._namespace = None
                area.mount(Static("[dim]Namespace cleared[/]"))
            elif parts[1] == "--all":
                self._namespace = "--all"
                area.mount(Static("[dim]Namespace set to: all namespaces[/]"))
            else:
                self._namespace = parts[1]
                area.mount(Static(f"[dim]Namespace set to: {self._namespace}[/]"))
            self._refresh_status()
        elif command == "/id":
            if self.session_id:
                area.mount(Static(f"[dim]Session: {self.session_id}[/]"))
            else:
                area.mount(Static("[dim]No active session -- send a message first[/]"))
        elif command == "/resume":
            if len(parts) < 2:
                area.mount(Static("[dim]Usage: /resume <session-id>[/]"))
            else:
                self._resume_chat(parts[1])
        elif command == "/status":
            self._refresh_status()
            area.mount(Static("[dim]Status refreshed[/]"))
        elif command == "/history":
            self._show_history()
        elif command == "/policy":
            if len(parts) >= 2 and parts[1].lower() == "reset":
                self._reset_policies()
            else:
                self._show_policies()
        elif command == "/theme":
            self._handle_theme(parts[1:])
        elif command in ("/quit", "/exit"):
            self.exit()
        elif command == "/help":
            self._show_help()
        else:
            cmd_name = command.lstrip("/")
            if cmd_name in self._commands:
                context = " ".join(parts[1:]).strip() if len(parts) > 1 else ""
                display = f"/{cmd_name}"
                if context:
                    display += f" {context}"
                area.mount(UserMessage(display))
                area.scroll_end(animate=False)
                self._stream_response(
                    context or self._commands[cmd_name].get("description", ""),
                    command=cmd_name,
                )
                return
            else:
                area.mount(Static(f"[dim]Unknown command: {command}[/]"))
        area.scroll_end(animate=False)

    @work(exclusive=False, thread=False)
    async def _show_help(self) -> None:
        area = self.query_one(ChatArea)

        if not self._commands:
            try:
                cmd_list = await self.client.get_commands()
                for cmd in cmd_list:
                    self._commands[cmd["name"]] = cmd
            except Exception:
                pass

        lines = [
            "TUI:",
            "  /help                Show this help",
            "  /ns <name|--all>     Set namespace",
            "  /clear               Clear chat and reset session",
            "  /id                  Show current session ID",
            "  /resume <id>         Resume a saved chat session",
            "  /status              Refresh status bar",
            "  /history             Show saved chats",
            "  /policy [reset]      View or reset tool policies",
            "  /theme [name]        View or change TUI theme",
            "  /quit, /exit         Exit the application",
            "  exit, quit           Exit (without slash)",
            "  !cmd                 Run a shell command directly",
            "",
            "Clipboard:",
            "  cmd+c / ctrl+c       Copy selected text",
            "  cmd+v / ctrl+v       Paste from system clipboard",
            "  Mouse drag           Select text, then copy",
            "  cmd+q / ctrl+q       Quit the application",
        ]
        if self._commands:
            lines.append("")
            lines.append("Slash commands:")
            for name, cmd in self._commands.items():
                desc = cmd.get("description", "")
                lines.append(f"  /{name:<34s} {desc}")
        area.mount(_info_block("Help", "[dim]" + "\n".join(lines) + "[/]"))
        area.scroll_end(animate=False)

    @work(exclusive=True, thread=False)
    async def _show_history(self) -> None:
        area = self.query_one(ChatArea)
        try:
            chats = await self.client.list_chats()
            if not chats:
                area.mount(Static("[dim]No saved chats[/]"))
            else:
                lines = ["[dim]Saved chats (use /resume <id> to continue):"]
                for c in chats[:20]:
                    lines.append(f"  {c['id'][:8]}  {c.get('title', '?')}")
                lines.append("[/]")
                area.mount(Static("\n".join(lines)))
        except Exception as exc:
            area.mount(ErrorMessage(str(exc)))

    @work(exclusive=False, thread=False)
    async def _show_policies(self) -> None:
        area = self.query_one(ChatArea)
        try:
            mcp_data = await self.client.get_mcp()
            lines = []
            for srv in mcp_data.get("servers", []):
                policy = srv.get("policy", {})
                srv_name = srv["name"]
                lines.append(f"  {srv_name}  (default: {policy.get('default', '?')})")
                tool_overrides = policy.get("tools", {})
                for t in srv.get("tools", []):
                    override = tool_overrides.get(t["name"])
                    if override:
                        lines.append(f"    {t['name']}: {override}")
            area.mount(
                _info_block(
                    "Tool Policies (/policy reset to restore defaults)",
                    "[dim]" + "\n".join(lines) + "[/]",
                )
            )
        except Exception as exc:
            area.mount(ErrorMessage(str(exc)))
        area.scroll_end(animate=False)

    @work(exclusive=False, thread=False)
    async def _reset_policies(self) -> None:
        area = self.query_one(ChatArea)
        try:
            await self.client.reset_policies()
            area.mount(Static("[dim]Policies reset to defaults[/]"))
        except Exception as exc:
            area.mount(ErrorMessage(str(exc)))
        area.scroll_end(animate=False)

    def _handle_theme(self, args: list[str]) -> None:
        area = self.query_one(ChatArea)
        themes = sorted(self.available_themes.keys())

        if not args:
            selector = OptionSelector(
                title="Select theme:",
                options=themes,
                current=self.theme,
            )
            area.mount(selector)
            area.scroll_end(animate=False)
            return

        name = args[0].lower()
        if name not in self.available_themes:
            area.mount(
                ErrorMessage(f"Unknown theme '{name}'. Use /theme to list available.")
            )
            area.scroll_end(animate=False)
            return

        self._apply_theme(name)

    def _apply_theme(self, name: str) -> None:
        area = self.query_one(ChatArea)
        self.theme = name
        save_tui_theme(name)
        area.mount(Static(f"[dim]Theme set to: {name} (saved)[/]"))
        area.scroll_end(animate=False)

    @work(exclusive=True, thread=False)
    async def _resume_chat(self, chat_id: str) -> None:
        area = self.query_one(ChatArea)
        try:
            chats = await self.client.list_chats()
            matches = [c for c in chats if c["id"].startswith(chat_id)]
            if not matches:
                area.mount(ErrorMessage(f"No chat found matching '{chat_id}'"))
                area.scroll_end(animate=False)
                return
            full_id = matches[0]["id"]
            chat = await self.client.get_chat(full_id)
            if not chat:
                area.mount(ErrorMessage(f"Chat '{full_id}' not found"))
                area.scroll_end(animate=False)
                return

            area.remove_children()
            self.session_id = full_id
            self._history.clear()

            for msg in chat.get("messages", []):
                role = msg.get("role")
                content = msg.get("content", "")
                if role == "user":
                    area.mount(UserMessage(content))
                    self._history.append(msg)
                elif role == "assistant":
                    area.mount(AssistantMessage(content))
                    self._history.append(msg)

            self._update_title()
            area.mount(
                Static(
                    f"[dim]Resumed session {full_id[:8]} -- {chat.get('title', '')}[/]"
                )
            )
        except Exception as exc:
            area.mount(ErrorMessage(str(exc)))
        area.scroll_end(animate=False)

    # -- option selector ------------------------------------------------------

    @on(OptionSelector.Selected)
    def on_option_selected(self, event: OptionSelector.Selected) -> None:
        """Handle option selector choice (e.g. theme picker)."""
        for selector in self.query(OptionSelector):
            selector.remove()
        self._apply_theme(event.value)
        try:
            self.query_one("#chat-input").focus()
        except Exception:
            pass

    # -- approval via arrow-key selector -------------------------------------

    @on(ApprovalPrompt.Responded)
    def on_approval_responded(self, event: ApprovalPrompt.Responded) -> None:
        """Handle the user's approve/reject selection."""
        if self._approval_event and not self._approval_event.is_set():
            self._approval_result = event.approved
            self._approval_always = event.always
            self._approval_event.set()

        for prompt in self.query(ApprovalPrompt):
            prompt.remove()

        if self._current_tool:
            if event.always:
                label = "Always Accept" if event.approved else "Always Reject"
            elif event.approved:
                label = "Approved"
            else:
                label = "Rejected"
            self._current_tool.set_approved(label)

        area = self.query_one(ChatArea)
        area.scroll_end(animate=False)

        try:
            self.query_one("#chat-input").focus()
        except Exception:
            pass

    # -- SSE streaming -------------------------------------------------------

    @work(exclusive=True, thread=False)
    async def _stream_response(self, message: str, command: str | None = None) -> None:
        area = self.query_one(ChatArea)
        self._history.append({"role": "user", "content": message})
        assistant_content = ""
        try:
            async for evt in self.client.stream_chat(
                message=message,
                session_id=self.session_id,
                history=self._history[:-1] or None,
                namespace=self._namespace,
                command=command,
            ):
                event_type = evt.get("event", "")

                if event_type == "session":
                    self.session_id = evt.get("session_id")
                    self._update_title()

                elif event_type == "thinking":
                    if not self._thinking:
                        self._thinking = ThinkingIndicator()
                        area.mount(self._thinking)
                        area.scroll_end(animate=False)

                elif event_type == "tool_call":
                    name = evt.get("name", "?")
                    args = evt.get("arguments")
                    args_short = ""
                    if args:
                        args_short = ", ".join(f"{k}={v!r}" for k, v in args.items())
                        if len(args_short) > 80:
                            args_short = args_short[:80] + "..."
                    if self._thinking:
                        self._thinking.add_tool_line(f"{name}({args_short})")
                    card = ToolCard(
                        name=name,
                        arguments=args,
                        pending=evt.get("pending", False),
                    )
                    self._current_tool = card
                    if self._thinking:
                        self._thinking.mount_tool_card(card)
                    else:
                        area.mount(card)
                    area.scroll_end(animate=False)

                    if evt.get("pending"):
                        logger.info("Awaiting approval for tool: %s", name)
                        await self._handle_approval(
                            evt.get("name", "?"), evt.get("arguments", {})
                        )
                        logger.info("Approval completed for tool: %s", name)

                elif event_type == "tool_result":
                    if self._current_tool:
                        self._current_tool.set_result(evt.get("result", ""))
                        self._current_tool = None

                elif event_type == "tool_rejected":
                    if self._current_tool:
                        self._current_tool.set_rejected(evt.get("reason", "rejected"))
                        self._current_tool = None

                elif event_type == "content":
                    self._remove_thinking()
                    assistant_content = evt.get("content", "")
                    if assistant_content:
                        md = AssistantMessage(assistant_content)
                        area.mount(md)
                        area.scroll_end(animate=False)

                elif event_type == "error":
                    self._remove_thinking()
                    area.mount(ErrorMessage(evt.get("message", "unknown error")))
                    area.scroll_end(animate=False)

        except Exception as exc:
            self._remove_thinking()
            logger.error("Stream error: %s: %s", type(exc).__name__, exc)
            area.mount(ErrorMessage(_friendly_error(exc)))
            area.scroll_end(animate=False)

        if assistant_content:
            self._history.append({"role": "assistant", "content": assistant_content})

    async def _handle_approval(self, name: str, arguments: dict) -> None:
        """Show an arrow-key selector for approve/reject and wait."""
        area = self.query_one(ChatArea)
        prompt = ApprovalPrompt(name, arguments)
        area.mount(prompt)
        area.scroll_end(animate=False)

        self._approval_event = asyncio.Event()
        self._approval_result = False
        self._approval_always = False
        self._approval_tool_name = name

        await self._approval_event.wait()

        approved = self._approval_result
        always = self._approval_always
        self._approval_event = None

        if always:
            try:
                if name == "bash":
                    cmd = arguments.get("command", "").strip()
                    prefix = cmd.split("|")[0].strip()
                    await self.client.add_bash_prefix(prefix, approved)
                else:
                    policy = "accept" if approved else "reject"
                    await self.client.set_tool_policy(name, policy)
            except Exception as exc:
                logger.warning("Failed to set tool policy: %s", exc)

        if self.session_id:
            try:
                await self.client.approve_tool(
                    self.session_id,
                    approved=approved,
                    reason="rejected by user" if not approved else None,
                )
            except Exception as exc:
                logger.warning("Approval call failed: %s", exc)

    def _remove_thinking(self) -> None:
        if self._thinking:
            self._thinking.finish()
            self._thinking = None

    def _update_title(self) -> None:
        if self.session_id:
            self.sub_title = f"session: {self.session_id[:8]}"
        else:
            self.sub_title = ""

    # -- actions -------------------------------------------------------------

    def action_clear(self) -> None:
        self.query_one(ChatArea).remove_children()
        self._history.clear()
        self.session_id = None
        self._update_title()

    async def action_quit(self) -> None:
        await self.client.close()
        self.exit()


def main():
    parser = argparse.ArgumentParser(description="mtv-agent TUI")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="Server URL (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    log_dir = Path.home() / ".mtv-agent"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
        filename=str(log_dir / "tui.log"),
        filemode="w",
    )
    app = MTVApp(server_url=args.server)
    app.run()


if __name__ == "__main__":
    main()
