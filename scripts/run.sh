#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

WITH_COP=false
for arg in "$@"; do
  case "$arg" in
    --with-cop) WITH_COP=true ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Prerequisites — resolve kube credentials (env vars > kubeconfig)
# ---------------------------------------------------------------------------

if [[ -z "${KUBE_API_URL:-}" ]] || [[ -z "${KUBE_TOKEN:-}" ]]; then
  KUBECONFIG_FILE="${KUBECONFIG:-$HOME/.kube/config}"
  if [[ -f "$KUBECONFIG_FILE" ]]; then
    echo "KUBE_API_URL or KUBE_TOKEN not set — reading from kubeconfig ($KUBECONFIG_FILE)..."
    if [[ -z "${KUBE_API_URL:-}" ]]; then
      KUBE_API_URL=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}' 2>/dev/null || true)
    fi
    if [[ -z "${KUBE_TOKEN:-}" ]]; then
      KUBE_TOKEN=$(kubectl config view --minify -o jsonpath='{.users[0].user.token}' 2>/dev/null || true)
    fi
    if [[ -z "${KUBE_TOKEN:-}" ]]; then
      KUBE_TOKEN=$(oc whoami -t 2>/dev/null || true)
    fi
  fi
fi

if [[ -z "${KUBE_API_URL:-}" ]]; then
  echo "Error: Kubernetes API URL not found."
  echo "  export KUBE_API_URL=https://api.cluster.example.com:6443"
  echo "  or configure a kubeconfig with 'oc login' / 'kubectl config'"
  exit 1
fi

if [[ -z "${KUBE_TOKEN:-}" ]]; then
  echo "Error: Kubernetes token not found."
  echo "  export KUBE_TOKEN=\$(oc whoami -t)"
  echo "  or configure a kubeconfig with 'oc login' / 'kubectl config'"
  exit 1
fi

# ---------------------------------------------------------------------------
# Container runtime (prefer docker, fall back to podman)
# ---------------------------------------------------------------------------

if command -v docker &>/dev/null; then
  RUNTIME=docker
elif command -v podman &>/dev/null; then
  RUNTIME=podman
else
  echo "Error: neither docker nor podman found in PATH."
  exit 1
fi

# ---------------------------------------------------------------------------
# Container names
# ---------------------------------------------------------------------------

MCP_MTV_NAME="mtv-agent-mcp-mtv"
MCP_METRICS_NAME="mtv-agent-mcp-metrics"
MCP_DEBUG_NAME="mtv-agent-mcp-debug-queries"
COP_PORT=1234

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

BGPIDS=()

cleanup() {
  echo ""
  echo "Shutting down..."
  for pid in "${BGPIDS[@]+"${BGPIDS[@]}"}"; do
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  done
  $RUNTIME stop "$MCP_MTV_NAME" 2>/dev/null || true
  $RUNTIME stop "$MCP_METRICS_NAME" 2>/dev/null || true
  $RUNTIME stop "$MCP_DEBUG_NAME" 2>/dev/null || true
  if [[ -n "${COP_PID:-}" ]]; then
    kill "$COP_PID" 2>/dev/null || true
    wait "$COP_PID" 2>/dev/null || true
  fi
  echo "Done."
}

trap cleanup EXIT

# ---------------------------------------------------------------------------
# Stop leftover containers from a previous run
# ---------------------------------------------------------------------------

$RUNTIME rm -f "$MCP_MTV_NAME" 2>/dev/null || true
$RUNTIME rm -f "$MCP_METRICS_NAME" 2>/dev/null || true
$RUNTIME rm -f "$MCP_DEBUG_NAME" 2>/dev/null || true

# ---------------------------------------------------------------------------
# Start MCP server containers
# ---------------------------------------------------------------------------

echo "Starting MCP servers ($RUNTIME)..."

$RUNTIME run --rm -d --name "$MCP_MTV_NAME" \
  -p 8080:8080 \
  -e MCP_KUBE_INSECURE=true \
  quay.io/yaacov/kubectl-mtv-mcp-server:latest >/dev/null

$RUNTIME run --rm -d --name "$MCP_METRICS_NAME" \
  -p 8081:8080 \
  -e MCP_KUBE_INSECURE=true \
  quay.io/yaacov/kubectl-metrics-mcp-server:latest >/dev/null

$RUNTIME run --rm -d --name "$MCP_DEBUG_NAME" \
  -p 8082:8080 \
  -e MCP_KUBE_INSECURE=true \
  quay.io/yaacov/kubectl-debug-queries-mcp-server:latest >/dev/null

echo "  kubectl-mtv            -> http://localhost:8080/sse"
echo "  kubectl-metrics        -> http://localhost:8081/sse"
echo "  kubectl-debug-queries  -> http://localhost:8082/sse"

# ---------------------------------------------------------------------------
# Optionally start claude-openai-proxy (OpenAI-compatible Claude proxy)
# ---------------------------------------------------------------------------

COP_PID=""
if $WITH_COP; then
  echo "Starting claude-openai-proxy on port $COP_PORT..."
  PORT=$COP_PORT uv run claude-openai-proxy &
  COP_PID=$!
  echo "  claude-openai-proxy -> http://localhost:${COP_PORT}"
fi

sleep 2

# ---------------------------------------------------------------------------
# Ensure config exists
# ---------------------------------------------------------------------------

if [[ ! -f config.json ]]; then
  cp config.json.example config.json
  echo "Created config.json from config.json.example"
fi

# ---------------------------------------------------------------------------
# Start the API server
# ---------------------------------------------------------------------------

echo "Starting API server..."
echo "  API server         -> http://localhost:8000"
echo ""
CONFIG=./config.json \
  uv run python -m mtv_agent serve \
  --kube-api-url "$KUBE_API_URL" \
  --kube-token "$KUBE_TOKEN"
