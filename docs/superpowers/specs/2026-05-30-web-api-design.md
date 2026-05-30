# Web API Design

**Date:** 2026-05-30
**Status:** Approved

## Overview

Serve today's digest as JSON over HTTP. A small FastAPI app exposes the saved
entries; `feedy serve` runs it with uvicorn. Day 25.

## Architecture

New dependencies: `fastapi`, `uvicorn` (added to `pyproject.toml`). Tests use
`fastapi.testclient.TestClient` (no live server needed).

## Components

### `feedy/web.py`

- `app = FastAPI(title="feedy", version="0.1.0")`
- `GET /` → `{"service": "feedy", "status": "ok"}` (health check)
- `GET /digest?since=&source=` → today's entries as JSON
  - `since` defaults to today (`YYYY-MM-DD`) when omitted.
  - Calls `storage.get_entries(source=source, since=since)`.
  - Returns `{"since": ..., "source": ..., "count": N, "entries": [...]}`.
  - `entries` are the storage dicts as-is (already JSON-serializable).

### `feedy/cli.py`

- `feedy serve --host 127.0.0.1 --port 8000` → `uvicorn.run(app, host=host, port=port)`.
- Imports `app` + `uvicorn` lazily inside the command so the heavy import only
  loads when serving.

## Tests

### `tests/test_web.py`
- `GET /` returns health JSON.
- `GET /digest` defaults `since` to today and calls `get_entries`.
- `GET /digest` returns entries + correct count.
- `since` and `source` query params passed through to `get_entries`.

### `tests/test_cli.py`
- `feedy serve` calls `uvicorn.run` with the chosen host/port.

## Out of Scope

- HTML rendering (JSON only)
- Authentication
- Pagination
- Triggering fetch/summarize from the API (read-only over stored entries)
