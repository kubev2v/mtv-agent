"""Internal 'bash' MCP server -- runs commands via subprocess."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)

MAX_OUTPUT = 50_000  # truncate long command output


class BashServer:
    """Internal MCP-like server that executes shell commands."""

    name = "bash"
    transport = "internal"
    connected = True

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": "bash",
                "description": "Run a shell command and return its output.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute.",
                        }
                    },
                    "required": ["command"],
                },
            }
        ]

    async def call_tool(self, _name: str, arguments: dict) -> str:
        command = arguments.get("command", "")
        if not command.strip():
            return "Error: empty command"
        logger.info("bash> %s", command)
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            output = stdout.decode(errors="replace")
            if len(output) > MAX_OUTPUT:
                output = output[:MAX_OUTPUT] + "\n... (truncated)"
            return output or "(no output)"
        except asyncio.TimeoutError:
            return "Error: command timed out after 120 seconds"
        except Exception as exc:
            return f"Error: {exc}"
