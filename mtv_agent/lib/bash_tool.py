"""Built-in bash tool -- runs shell commands and returns output."""

import asyncio
import logging

from mtv_agent.lib.text_utils import DEFAULT_TRUNCATE_LIMIT, truncate

logger = logging.getLogger(__name__)

TOOL_NAME = "bash"
DEFAULT_TIMEOUT_SECONDS = 120

BASH_TRUNCATE_HINT = (
    "Try filtering or limiting results, e.g. grep, --selector, "
    "-l, --limit, jq, head/tail, or narrower queries to get more "
    "relevant output."
)

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": (
            "Fallback tool: run a bash command and return its stdout and stderr. "
            "Only use this when no specialized MCP tool can accomplish the task. "
            "Suitable for arbitrary shell commands such as curl, jq, python3, "
            "or other CLI tools not covered by available MCP tools."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute.",
                },
            },
            "required": ["command"],
        },
    },
}


async def run(command: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """Execute *command* in a bash shell and return combined output."""
    logger.info("bash: %s", command)
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            shell=True,
            executable="/bin/bash",
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = stdout.decode(errors="replace").strip()
        if proc.returncode != 0:
            output = f"[exit code {proc.returncode}]\n{output}"
        if not output:
            return "(no output)"
        return truncate(output, DEFAULT_TRUNCATE_LIMIT, BASH_TRUNCATE_HINT)
    except asyncio.TimeoutError:
        proc.kill()
        return f"[error] Command timed out after {timeout}s"
    except Exception as exc:
        return f"[error] {exc}"
