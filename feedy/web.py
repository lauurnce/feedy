from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI

import feedy.storage as storage

app = FastAPI(title="feedy", version="0.1.0")


@app.get("/")
def root() -> dict:
    """Health check."""
    return {"service": "feedy", "status": "ok"}


@app.get("/digest")
def digest(since: str | None = None, source: str | None = None) -> dict:
    """Return saved entries as JSON. `since` defaults to today."""
    if since is None:
        since = datetime.now().strftime("%Y-%m-%d")
    entries = storage.get_entries(source=source, since=since)
    return {
        "since": since,
        "source": source,
        "count": len(entries),
        "entries": entries,
    }
