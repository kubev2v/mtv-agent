"""FastAPI application -- routes, SSE streaming, and clean lifespan."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from mtv_agent.server.agent import run_stream
from mtv_agent.server.chat.store import ChatStore
from mtv_agent.server.commands import load_commands
from mtv_agent.server.config import Settings, load_settings
from mtv_agent.server.llm.client import LLMClient, discover_model
from mtv_agent.server.llm.prompt import build_system_prompt
from mtv_agent.server.mcp.manager import MCPManager

logger = logging.getLogger(__name__)

_ERROR_FILE = Path.home() / ".mtv-agent" / "startup.error"


def _write_startup_error(msg: str) -> None:
    """Write a clean error message for the CLI launcher to display."""
    try:
        _ERROR_FILE.parent.mkdir(parents=True, exist_ok=True)
        _ERROR_FILE.write_text(msg)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Shared state (initialised in _cmd_serve / lifespan, not at import time)
# ---------------------------------------------------------------------------

settings: Settings = Settings()
mcp: MCPManager = MCPManager()
store: ChatStore | None = None
llm: LLMClient | None = None
system_prompt = ""
commands: dict[str, dict] = {}

# Per-session approval queues: session_id -> Queue
_approval_queues: dict[str, asyncio.Queue] = {}
# Per-session cancel events
_cancel_events: dict[str, asyncio.Event] = {}


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global llm, store

    store = ChatStore(settings.cache_dir)

    model = settings.llm_model
    if not model:
        try:
            model = await discover_model(settings.llm_base_url, settings.llm_api_key)
            logger.info("Discovered model: %s", model)
        except Exception as exc:
            msg = (
                f"Could not connect to LLM at {settings.llm_base_url}\n"
                f"  {exc}\n\n"
                f"Check config.json 'llm.baseUrl' and ensure the LLM server is running."
            )
            _write_startup_error(msg)
            raise SystemExit(1) from None

    dump_dir = (
        str(Path(settings.dump_http_dir).expanduser()) if settings.dump_http else None
    )
    llm = LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=model,
        dump_dir=dump_dir,
    )

    try:
        await mcp.start(
            mcp_config=settings.mcp_config,
            skills_dir=settings.skills_dir,
        )
    except SystemExit as exc:
        _write_startup_error(str(exc))
        raise
    except RuntimeError as exc:
        _write_startup_error(str(exc))
        raise SystemExit(1) from None

    global system_prompt
    system_prompt = build_system_prompt(mcp.get_tool_definitions())

    global commands
    commands = load_commands(settings.commands_dir)

    _ERROR_FILE.unlink(missing_ok=True)
    logger.info("Server ready -- model=%s", model)

    yield

    try:
        await mcp.stop()
    except BaseException:
        pass


app = FastAPI(title="mtv-agent", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/status")
async def status():
    servers_info = mcp.get_servers()
    tool_count = sum(len(s["tools"]) for s in servers_info["servers"])
    return {
        "model": llm.model if llm else "unknown",
        "servers": len(servers_info["servers"]),
        "tools": tool_count,
    }


@app.get("/api/mcp")
async def get_mcp():
    return mcp.get_servers()


@app.put("/api/mcp")
async def put_mcp(request: Request):
    data = await request.json()
    mcp.update_policies(data)
    return mcp.get_servers()


@app.get("/api/commands")
async def list_commands():
    return [
        {"name": name, "description": cmd["description"], "category": cmd["category"]}
        for name, cmd in commands.items()
    ]


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "").strip()
    session_id = body.get("session_id") or str(uuid.uuid4())
    history = body.get("history")
    namespace = body.get("namespace")
    command_name = body.get("command")

    command_body = None
    if command_name and command_name in commands:
        command_body = commands[command_name]["body"]
        if not message:
            message = commands[command_name]["description"]

    if not message:
        raise HTTPException(400, "message is required")
    if not llm:
        raise HTTPException(502, "LLM not initialised")

    # Bang command: run shell directly
    if message.startswith("!"):
        cmd = message[1:].strip()
        return EventSourceResponse(_bang_stream(session_id, cmd))

    approval_q: asyncio.Queue = asyncio.Queue()
    cancel_evt = asyncio.Event()
    _approval_queues[session_id] = approval_q
    _cancel_events[session_id] = cancel_evt

    async def approve_fn(name: str, args: dict) -> tuple[bool, str | None]:
        result = await approval_q.get()
        return result.get("approved", False), result.get("reason")

    async def event_generator():
        all_messages = list(history or [])
        all_messages.append({"role": "user", "content": message})
        assistant_content = ""
        try:
            yield {
                "event": "session",
                "data": json.dumps({"session_id": session_id}),
            }
            async for evt in run_stream(
                message=message,
                llm=llm,
                mcp=mcp,
                system_prompt=system_prompt,
                approve_fn=approve_fn,
                history=history,
                namespace=namespace,
                command=command_body,
                session_id=session_id,
                max_iterations=settings.max_iterations,
                max_history_chars=settings.max_history_chars,
            ):
                if cancel_evt.is_set():
                    yield {
                        "event": "error",
                        "data": json.dumps({"message": "cancelled"}),
                    }
                    return
                event_name = evt.pop("event")
                if event_name == "_messages_snapshot":
                    all_messages = evt["messages"]
                    continue
                if event_name == "content":
                    assistant_content = evt.get("content", "")
                yield {
                    "event": event_name,
                    "data": json.dumps(evt),
                }
        except Exception as exc:
            logger.exception("SSE stream error for session %s", session_id)
            yield {
                "event": "error",
                "data": json.dumps({"message": str(exc)}),
            }
        finally:
            _approval_queues.pop(session_id, None)
            _cancel_events.pop(session_id, None)
            if assistant_content:
                if not any(
                    m.get("role") == "assistant"
                    and m.get("content") == assistant_content
                    for m in all_messages[-1:]
                ):
                    all_messages.append(
                        {"role": "assistant", "content": assistant_content}
                    )
                try:
                    store.save(session_id, all_messages)
                except Exception:
                    logger.warning("Failed to save chat %s", session_id)

    return EventSourceResponse(event_generator(), ping=15)


@app.post("/api/chat/{session_id}/cancel")
async def cancel_chat(session_id: str):
    evt = _cancel_events.get(session_id)
    if not evt:
        raise HTTPException(404, "No active session")
    evt.set()
    return {"status": "cancelled"}


@app.post("/api/chat/{session_id}/approve")
async def approve_tool(session_id: str, request: Request):
    q = _approval_queues.get(session_id)
    if not q:
        raise HTTPException(404, "No active session or no pending approval")
    body = await request.json()
    await q.put(body)
    return {"status": "ok"}


@app.get("/api/chats")
async def list_chats():
    return store.list()


@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    chat = store.get(chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    return chat


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    if not store.delete(chat_id):
        raise HTTPException(404, "Chat not found")
    return {"status": "deleted"}


# ---------------------------------------------------------------------------
# Bang command helper
# ---------------------------------------------------------------------------


async def _bang_stream(session_id: str, cmd: str):
    yield {
        "event": "session",
        "data": json.dumps({"session_id": session_id}),
    }
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
        output = stdout.decode(errors="replace")
    except asyncio.TimeoutError:
        output = "Error: command timed out"
    except Exception as exc:
        output = f"Error: {exc}"
    yield {
        "event": "content",
        "data": json.dumps({"content": f"```\n{output}\n```"}),
    }


# ---------------------------------------------------------------------------
# CLI subcommands
# ---------------------------------------------------------------------------


def main():
    """Entry point for mtv-server -- starts the API server."""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
    )

    global settings, store
    try:
        settings = load_settings()
    except SystemExit as exc:
        sys.stderr.write(f"\n{exc}\n")
        _write_startup_error(str(exc))
        raise SystemExit(1) from None

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
