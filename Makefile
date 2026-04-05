.PHONY: help install test fetch digest sources stats clean

help:
	@grep -E '^[a-z-]+:' $(MAKEFILE_LIST) | cut -d: -f1 | sort

install:
	uv sync

test:
	uv run pytest -q

fetch:
	uv run feedy fetch
