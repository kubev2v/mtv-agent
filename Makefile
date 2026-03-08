.DEFAULT_GOAL := help
.PHONY: run run-cop dev serve build-web dev-web stop format format-web lint lint-web package help

## Run the full stack via scripts/run.sh (dev)
run:
	@scripts/run.sh

## Run with COP via scripts/run.sh (dev)
run-cop:
	@scripts/run.sh --with-cop

## Run API server with --no-web for frontend dev
dev:
	@NO_WEB=1 scripts/run.sh

## Start only the API server (pip-installed entrypoint)
serve:
	CONFIG=./config.json uv run python -m mtv_agent serve

## Build the web UI into web/dist
build-web:
	cd web && npm ci && npm run build

## Start the Vite dev server for the web UI
dev-web:
	cd web && npm run dev

## Stop all MCP containers and proxy
stop:
	@echo "Stopping MCP containers..."
	@docker stop mtv-agent-mcp-mtv 2>/dev/null || podman stop mtv-agent-mcp-mtv 2>/dev/null || true
	@docker stop mtv-agent-mcp-metrics 2>/dev/null || podman stop mtv-agent-mcp-metrics 2>/dev/null || true
	@docker stop mtv-agent-mcp-debug-queries 2>/dev/null || podman stop mtv-agent-mcp-debug-queries 2>/dev/null || true
	@echo "Stopping claude-openai-proxy (if running)..."
	@pkill -f 'claude_openai_proxy' 2>/dev/null || true
	@echo "Done."

## Format Python code with ruff
format:
	uv run ruff format .
	uv run ruff check --fix .

## Format web code with prettier
format-web:
	cd web && npm run format

## Lint Python code with ruff
lint:
	uv run ruff check .
	uv run ruff format --check .

## Lint web code with eslint and prettier
lint-web:
	cd web && npm run lint && npm run format:check

## Build pip-distributable package (includes web UI)
package: build-web
	rm -rf mtv_agent/web_dist
	cp -r web/dist mtv_agent/web_dist
	rm -rf mtv_agent/data/skills mtv_agent/data/playbooks
	cp -r skills mtv_agent/data/skills
	cp -r playbooks mtv_agent/data/playbooks
	uv build

## Show this help
help:
	@grep -B1 -E '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) \
	  | grep -v '^\-\-$$' \
	  | awk '/^##/ {desc=substr($$0,4)} /^[a-zA-Z_-]+:/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, desc; desc=""}'
