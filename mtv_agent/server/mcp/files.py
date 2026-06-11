"""Internal 'files' MCP server -- list, read, and write files."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_OUTPUT = 50_000  # truncate long file content


class FilesServer:
    """Internal MCP-like server for filesystem operations."""

    name = "files"
    transport = "internal"
    connected = True

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": "list_files",
                "description": (
                    "List files and directories at a given path. "
                    "Directories are shown with a trailing '/' suffix."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list (defaults to '.').",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "List recursively (default false).",
                        },
                    },
                },
            },
            {
                "name": "read_file",
                "description": "Read the contents of a file and return it as text.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read.",
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Line number to start reading from (1-based).",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of lines to return.",
                        },
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "write_file",
                "description": "Write content to a file, creating it if it does not exist or overwriting if it does.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to write.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file.",
                        },
                    },
                    "required": ["path", "content"],
                },
            },
        ]

    async def call_tool(self, name: str, arguments: dict) -> str:
        if name == "list_files":
            return self._list_files(arguments)
        elif name == "read_file":
            return self._read_file(arguments)
        elif name == "write_file":
            return self._write_file(arguments)
        return f"Unknown tool: {name}"

    def _list_files(self, arguments: dict) -> str:
        target = Path(arguments.get("path", "."))
        recursive = arguments.get("recursive", False)

        if not target.exists():
            return f"Error: path not found: {target}"
        if not target.is_dir():
            return f"Error: not a directory: {target}"

        try:
            entries = []
            if recursive:
                for item in sorted(target.rglob("*")):
                    rel = item.relative_to(target)
                    entries.append(f"{rel}/" if item.is_dir() else str(rel))
            else:
                for item in sorted(target.iterdir()):
                    entries.append(f"{item.name}/" if item.is_dir() else item.name)
            return "\n".join(entries) if entries else "(empty directory)"
        except PermissionError:
            return f"Error: permission denied: {target}"
        except Exception as exc:
            return f"Error: {exc}"

    def _read_file(self, arguments: dict) -> str:
        path_str = arguments.get("path", "")
        if not path_str:
            return "Error: path is required"

        target = Path(path_str)
        if not target.exists():
            return f"Error: file not found: {target}"
        if not target.is_file():
            return f"Error: not a file: {target}"

        try:
            text = target.read_text(errors="replace")

            offset = arguments.get("offset")
            limit = arguments.get("limit")

            if offset is not None or limit is not None:
                lines = text.splitlines(keepends=True)
                start = max((offset or 1) - 1, 0)
                end = start + limit if limit else len(lines)
                text = "".join(lines[start:end])

            if len(text) > MAX_OUTPUT:
                text = text[:MAX_OUTPUT] + "\n... (truncated)"
            return text if text else "(empty file)"
        except PermissionError:
            return f"Error: permission denied: {target}"
        except Exception as exc:
            return f"Error: {exc}"

    def _write_file(self, arguments: dict) -> str:
        path_str = arguments.get("path", "")
        if not path_str:
            return "Error: path is required"

        content = arguments.get("content")
        if content is None:
            return "Error: content is required"

        target = Path(path_str)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            logger.info("write_file> %s (%d bytes)", target, len(content))
            return f"Successfully wrote {len(content)} bytes to {target}"
        except PermissionError:
            return f"Error: permission denied: {target}"
        except Exception as exc:
            return f"Error: {exc}"
