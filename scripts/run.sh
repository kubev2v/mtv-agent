#!/usr/bin/env bash
# Thin wrapper around the Python CLI – all logic lives in
# mtv_agent.orchestrator.start_all().
set -euo pipefail

ARGS=()
for arg in "$@"; do
  case "$arg" in
    --with-cop) ARGS+=(--with-cop) ;;
    --no-web)   ARGS+=(--no-web) ;;
    *)          ARGS+=("$arg") ;;
  esac
done

exec uv run python -m mtv_agent start "${ARGS[@]}"
