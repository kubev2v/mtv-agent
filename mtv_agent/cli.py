"""Single command that starts the server as a subprocess then launches the TUI."""

from __future__ import annotations

import argparse
import atexit
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx

_ERROR_FILE = Path.home() / ".mtv-agent" / "startup.error"


def _wait_for_server(url: str, proc: subprocess.Popen, timeout: float = 30.0) -> bool:
    """Poll the server until it responds, or detect early process death."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False
        try:
            r = httpx.get(f"{url}/api/status", timeout=2.0)
            if r.status_code == 200:
                return True
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        time.sleep(0.3)
    return False


def _show_server_error() -> None:
    """Show the startup error file if it exists, otherwise a generic message."""
    msg = ""
    if _ERROR_FILE.is_file():
        try:
            msg = _ERROR_FILE.read_text().strip()
        except OSError:
            pass

    if msg:
        sys.stderr.write(f"\n{msg}\n")
    else:
        sys.stderr.write("\nServer failed to start -- check ~/.mtv-agent/server.log\n")
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def _cmd_run(args: argparse.Namespace) -> None:
    """Start server + TUI."""
    from mtv_agent.server.config import load_settings

    try:
        load_settings()
    except SystemExit as exc:
        sys.stderr.write(f"\n{exc}\n")
        raise SystemExit(1) from None

    base_url = f"http://127.0.0.1:{args.port}"
    try:
        httpx.get(f"{base_url}/api/status", timeout=1.0)
        sys.stderr.write(
            f"\nError: a server is already running on port {args.port}.\n"
            f"Stop it first, or use --port to choose a different port.\n"
        )
        raise SystemExit(1)
    except (httpx.ConnectError, httpx.TimeoutException):
        pass

    log_path = os.path.expanduser("~/.mtv-agent/server.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    _ERROR_FILE.unlink(missing_ok=True)

    log_file = open(log_path, "w")  # noqa: SIM115
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "mtv_agent.server.app",
        ],
        stdout=log_file,
        stderr=log_file,
        env={
            **os.environ,
            "MTV_AGENT_HOST": "127.0.0.1",
            "MTV_AGENT_PORT": str(args.port),
            **(
                {"MTV_AGENT_DUMP_HTTP": "1"}
                if args.dump_http or args.dump_http_dir
                else {}
            ),
            **(
                {"MTV_AGENT_DUMP_HTTP_DIR": args.dump_http_dir}
                if args.dump_http_dir
                else {}
            ),
        },
    )

    def _cleanup():
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        log_file.close()

    atexit.register(_cleanup)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    if not _wait_for_server(base_url, proc):
        _cleanup()
        _show_server_error()

    tui_log = os.path.expanduser("~/.mtv-agent/tui.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
        filename=tui_log,
        filemode="w",
    )

    from mtv_agent.tui.app import MTVApp

    app = MTVApp(server_url=base_url, resume_id=getattr(args, "resume", None))
    app.run()

    if app.session_id:
        sys.stderr.write(
            f"\nTo resume this session:\n"
            f"  mtv-agent run --resume {app.session_id[:8]}\n\n"
        )


def _cmd_init(args: argparse.Namespace) -> None:
    """Initialise ~/.mtv-agent/ with config, skills, and commands."""
    from mtv_agent.server.init import init_workspace

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    target = Path(args.dir) if args.dir else None
    init_workspace(target, force=args.force)


def _cmd_config(_args: argparse.Namespace) -> None:
    """Print default config.json to stdout."""
    from mtv_agent.server.config import bundled_config_example

    path = bundled_config_example()
    if path.is_file():
        sys.stdout.write(path.read_text(encoding="utf-8"))
    else:
        sys.stderr.write(f"Bundled config not found: {path}\n")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="mtv-agent",
        description="mtv-agent -- AI assistant for MTV/Forklift migrations",
    )

    sub = parser.add_subparsers(dest="command")

    # -- run (default) -------------------------------------------------------
    p_run = sub.add_parser("run", help="Start server + TUI (default)")
    p_run.add_argument(
        "--port", type=int, default=8000, help="Server port (default: 8000)"
    )
    p_run.add_argument(
        "--resume",
        metavar="ID",
        default=None,
        help="Resume a saved chat session by ID (prefix match)",
    )
    p_run.add_argument(
        "--dump-http",
        action="store_true",
        default=False,
        help="Dump LLM HTTP requests and responses to ~/.mtv-agent/dumps/",
    )
    p_run.add_argument(
        "--dump-http-dir",
        metavar="DIR",
        default=None,
        help="Directory for HTTP dump files (implies --dump-http)",
    )
    p_run.set_defaults(func=_cmd_run)

    # -- init ----------------------------------------------------------------
    p_init = sub.add_parser(
        "init",
        help="Create ~/.mtv-agent/ with config, skills, and commands",
    )
    p_init.add_argument(
        "--dir", default=None, help="Target directory (default: ~/.mtv-agent)"
    )
    p_init.add_argument(
        "--force", action="store_true", help="Overwrite existing config files"
    )
    p_init.set_defaults(func=_cmd_init)

    # -- config --------------------------------------------------------------
    p_config = sub.add_parser("config", help="Print default config.json to stdout")
    p_config.set_defaults(func=_cmd_config)

    # -- dispatch ------------------------------------------------------------
    args, remaining = parser.parse_known_args()
    if not hasattr(args, "func"):
        args = parser.parse_args(["run"] + remaining)

    args.func(args)


if __name__ == "__main__":
    main()
