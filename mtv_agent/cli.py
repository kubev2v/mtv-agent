"""Command-line interface for mtv-agent."""

from __future__ import annotations

import argparse
import logging
import sys

from mtv_agent import __version__


def _cmd_start(args: argparse.Namespace) -> None:
    """Start the full stack: MCP containers + optional COP + API server."""
    from mtv_agent.orchestrator import start_all

    start_all(
        with_cop=args.with_cop,
        config_path=args.config,
        mcp_config_path=args.mcp_config,
        runtime=args.runtime,
        host=args.host,
        port=args.port,
        no_web=args.no_web,
        skip_tls=args.skip_tls,
        kube_api_url=args.kube_api_url,
        kube_token=args.kube_token,
        kubeconfig=args.kubeconfig,
        kube_context=args.kube_context,
        open_browser=args.open,
    )


def _cmd_serve(args: argparse.Namespace) -> None:
    """Start only the API server."""
    from mtv_agent.orchestrator import serve

    serve(
        host=args.host,
        port=args.port,
        config_path=args.config,
        mcp_config_path=args.mcp_config,
        no_web=args.no_web,
        kube_api_url=args.kube_api_url,
        kube_token=args.kube_token,
        kubeconfig=args.kubeconfig,
        kube_context=args.kube_context,
        open_browser=args.open,
    )


def _cmd_stop(args: argparse.Namespace) -> None:
    """Stop MCP containers and claude-openai-proxy."""
    from mtv_agent.orchestrator import stop_cop_by_name, stop_mcp_containers_any_runtime

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Stopping MCP containers...")
    stop_mcp_containers_any_runtime()
    logger.info("Stopping claude-openai-proxy (if running)...")
    stop_cop_by_name()
    logger.info("Done.")


def _cmd_init(args: argparse.Namespace) -> None:
    """Initialise a local workspace with config, skills, and playbooks."""
    from pathlib import Path

    from mtv_agent.orchestrator import init_workspace

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    target = Path(args.dir) if args.dir else None
    init_workspace(target, force=args.force)


def _cmd_config(args: argparse.Namespace) -> None:
    """Print default configuration to stdout."""
    from mtv_agent.orchestrator import get_default_config_text

    sys.stdout.write(get_default_config_text())


def _add_kube_flags(parser: argparse.ArgumentParser) -> None:
    """Add the four Kubernetes credential flags shared by ``start`` and ``serve``."""
    parser.add_argument(
        "--kube-api-url",
        default=None,
        help="Kubernetes API server URL (overrides env and kubeconfig)",
    )
    parser.add_argument(
        "--kube-token",
        default=None,
        help="Kubernetes bearer token (overrides env and kubeconfig)",
    )
    parser.add_argument(
        "--kubeconfig",
        default=None,
        help="Path to kubeconfig file (default: $KUBECONFIG or ~/.kube/config)",
    )
    parser.add_argument(
        "--kube-context",
        default=None,
        help="Kubeconfig context to use (default: current-context)",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mtv-agent",
        description="AI agent for MTV/Forklift VM migrations",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    sub = parser.add_subparsers(dest="command")

    # -- start ---------------------------------------------------------------
    p_start = sub.add_parser(
        "start",
        help="Start MCP containers, optional LLM proxy, and the API server",
    )
    p_start.add_argument(
        "--with-cop",
        action="store_true",
        help="Also start claude-openai-proxy (Claude as LLM)",
    )
    p_start.add_argument(
        "--runtime",
        choices=["docker", "podman"],
        default=None,
        help="Container runtime (auto-detected if omitted)",
    )
    p_start.add_argument("--host", default=None, help="API server bind address")
    p_start.add_argument("--port", type=int, default=None, help="API server port")
    p_start.add_argument("--config", default=None, help="Path to config.json")
    p_start.add_argument("--mcp-config", default=None, help="Path to mcp.json")
    p_start.add_argument(
        "--no-web",
        action="store_true",
        help="Do not serve the static web UI (for frontend dev with Vite)",
    )
    p_start.add_argument(
        "--open",
        action="store_true",
        help="Open the web UI in a browser when the server is ready",
    )
    p_start.add_argument(
        "--skip-tls",
        action="store_true",
        help="Skip TLS certificate verification when pulling container images",
    )
    _add_kube_flags(p_start)
    p_start.set_defaults(func=_cmd_start)

    # -- serve ---------------------------------------------------------------
    p_serve = sub.add_parser(
        "serve",
        help="Start only the API server (MCP/LLM must be running separately)",
    )
    p_serve.add_argument("--host", default=None, help="API server bind address")
    p_serve.add_argument("--port", type=int, default=None, help="API server port")
    p_serve.add_argument("--config", default=None, help="Path to config.json")
    p_serve.add_argument("--mcp-config", default=None, help="Path to mcp.json")
    p_serve.add_argument(
        "--no-web",
        action="store_true",
        help="Do not serve the static web UI (for frontend dev with Vite)",
    )
    p_serve.add_argument(
        "--open",
        action="store_true",
        help="Open the web UI in a browser when the server is ready",
    )
    _add_kube_flags(p_serve)
    p_serve.set_defaults(func=_cmd_serve)

    # -- stop ----------------------------------------------------------------
    p_stop = sub.add_parser(
        "stop",
        help="Stop MCP containers and claude-openai-proxy",
    )
    p_stop.set_defaults(func=_cmd_stop)

    # -- init ----------------------------------------------------------------
    p_init = sub.add_parser(
        "init",
        help="Create a local workspace with config, skills, and playbooks",
    )
    p_init.add_argument(
        "--dir",
        default=None,
        help="Target directory (default: ~/.mtv-agent)",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    p_init.set_defaults(func=_cmd_init)

    # -- config --------------------------------------------------------------
    p_config = sub.add_parser(
        "config",
        help="Print default config.json to stdout",
    )
    p_config.set_defaults(func=_cmd_config)

    # -- dispatch ------------------------------------------------------------
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    if args.command in ("start", "serve"):
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s  %(name)s  %(message)s",
        )

    args.func(args)
