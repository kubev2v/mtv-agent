.DEFAULT_GOAL := help
.PHONY: run run-cop run-dev serve stop web-build web-dev format format-web lint lint-web package clean clean-all help

##@ Stack

## Run the full stack (MCP containers + API server)
run:
	@uv run python -m mtv_agent start

## Run the full stack with claude-openai-proxy
run-cop:
	@uv run python -m mtv_agent start --with-cop

## Run the full stack without static web UI (for frontend dev with Vite)
run-dev:
	@uv run python -m mtv_agent start --no-web

## Start only the API server (pip-installed entrypoint)
serve:
	uv run python -m mtv_agent serve --config ./config.json --mcp-config ./mcp.json

## Stop all MCP containers and proxy
stop:
	@uv run python -m mtv_agent stop

##@ Web UI

## Build the web UI into web/dist
web-build:
	cd web && npm ci && npm run build

## Start the Vite dev server for the web UI
web-dev:
	cd web && npm run dev

##@ Code Quality

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

##@ Packaging

## Build pip-distributable package (includes web UI)
package: web-build
	rm -rf mtv_agent/web_dist
	cp -r web/dist mtv_agent/web_dist
	rm -f mtv_agent/data/config.json.example mtv_agent/data/mcp.json.example
	uv build

## Remove build artifacts
clean:
	rm -rf dist/ mtv_agent/web_dist/ web/dist/ *.egg-info

## Remove build artifacts, caches, and node_modules
clean-all: clean
	rm -rf __pycache__ .ruff_cache web/node_modules

##@ Help

## Show this help
help:
	@awk '\
	  /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
	  /^##[^@]/ { desc = substr($$0, 4) } \
	  /^[a-zA-Z_-]+:/ { if (desc) { printf "  \033[36m%-15s\033[0m %s\n", $$1, desc; desc="" } }' $(MAKEFILE_LIST)
