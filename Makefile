.PHONY: help install test fetch digest sources stats clean

help:
	@grep -E '^[a-z-]+:' $(MAKEFILE_LIST) | cut -d: -f1 | sort

install:
	uv sync

test:
	uv run pytest -q

fetch:
	uv run feedy fetch

digest:
	uv run feedy digest

sources:
	uv run feedy sources

stats:
	uv run feedy stats

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
