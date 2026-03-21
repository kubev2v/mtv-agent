.DEFAULT_GOAL := help
.PHONY: run run-cop dev serve build-web dev-web stop format format-web lint lint-web package help

## Run the full stack (MCP containers + API server)
run:
	@uv run python -m mtv_agent start

## Run the full stack with claude-openai-proxy
run-cop:
	@uv run python -m mtv_agent start --with-cop

## Run the full stack without static web UI (for frontend dev with Vite)
dev:
	@uv run python -m mtv_agent start --no-web

## Start only the API server (pip-installed entrypoint)
serve:
	uv run python -m mtv_agent serve --config ./config.json --mcp-config ./mcp.json

## Build the web UI into web/dist
build-web:
	cd web && npm ci && npm run build

## Start the Vite dev server for the web UI
dev-web:
	cd web && npm run dev

## Stop all MCP containers and proxy
stop:
	@uv run python -m mtv_agent stop

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
	cp config.json.example mtv_agent/data/config.json.example
	cp mcp.json.example mtv_agent/data/mcp.json.example
	uv build

## Show this help
help:
	@grep -B1 -E '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) \
	  | grep -v '^\-\-$$' \
	  | awk '/^##/ {desc=substr($$0,4)} /^[a-zA-Z_-]+:/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, desc; desc=""}'
