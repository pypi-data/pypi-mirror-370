.PHONY: help install test lint format run

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

test:  ## Run all tests
	uv run pytest

test-unit:  ## Run unit tests only
	uv run pytest tests/unit -v

test-integration:  ## Run integration tests only
	uv run pytest tests/integration -v

test-e2e:  ## Run e2e tests only
	uv run pytest tests/e2e -v

lint:  ## Run linter
	uv run ruff check src tests

format:  ## Format code
	uv run ruff format src tests

run:  ## Run application locally
	uv run python -m src