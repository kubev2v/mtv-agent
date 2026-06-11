.PHONY: help build clean cleandist format lint test
.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

build: cleandist ## Build the package into dist/
	uv build

clean: ## Remove caches and egg-info
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache *.egg-info

cleandist: clean ## Remove dist/ and all cached artifacts
	rm -rf dist

format: ## Format code with ruff
	uv run ruff format mtv_agent tests

lint: ## Lint code with ruff
	uv run ruff check mtv_agent tests

test: ## Run tests with pytest
	uv run pytest tests/

