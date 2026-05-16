# SQLite Storage Module — Day 03 Design

**Date:** 2026-05-17
**Scope:** `feedy/storage.py` — save, dedup by URL, batch save, summary update

---

## Architecture

Single module, module-level functions, SQLite via Python stdlib `sqlite3`.
DB stored at `~/.feedy/feedy.db`. No ORM, no third-party dependencies.

---

## Schema

```sql
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT UNIQUE NOT NULL,
    title       TEXT,
    date        TEXT,
    source      TEXT,
    summary     TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
)
```

`url` carries a `UNIQUE` constraint — this is the dedup mechanism.

---

## Components

### `_connect() -> sqlite3.Connection`

- Creates `~/.feedy/` directory if missing
- Calls `init_db()` lazily (lazy init — callers never call it directly)
- Sets `conn.row_factory = sqlite3.Row`

### `init_db() -> None`

- `CREATE TABLE IF NOT EXISTS entries (...)` — idempotent, safe to call multiple times
- Called exclusively via `_connect()`; not part of the public API

### `save(entry: FeedEntry) -> bool`

- `INSERT INTO entries (url, title, date, source, summary) VALUES (?, ?, ?, ?, ?)`
- Catches `sqlite3.IntegrityError` for duplicate URLs
- Returns `True` if inserted, `False` if duplicate (skipped)

### `save_many(entries: list[FeedEntry]) -> tuple[int, int]`

- Calls `save()` per entry, accumulates results
- Returns `(saved_count, skipped_count)`
- Primary intake point for `BaseFeedSource.run()` output

### `all_entries() -> list[dict]`

- `SELECT * FROM entries ORDER BY created_at DESC`
- Returns `list[dict]` (via `sqlite3.Row` → `dict` conversion)

### `update_summary(url: str, summary: str) -> bool`

- `UPDATE entries SET summary = ? WHERE url = ?`
- Returns `True` if row was found and updated (`rowcount > 0`)
- Returns `False` if URL not in DB

---

## Data Flow

```
BaseFeedSource.run()
  └─► list[FeedEntry]
        └─► save_many(entries) → (saved, skipped)

AI summarizer (Day 11+)
  └─► update_summary(url, summary) → bool
```

---

## Error Handling

| Scenario | Handling |
|---|---|
| Duplicate URL on `save()` | Catch `IntegrityError`, return `False` |
| URL not found on `update_summary()` | Check `cursor.rowcount == 0`, return `False` |
| DB directory missing | `Path.mkdir(parents=True, exist_ok=True)` in `_connect()` |

No retry logic. `sqlite3` stdlib is reliable for single-process use.

---

## Testing (Day 05)

Monkey-patch `feedy.storage.DB_PATH` to `tmp_path / "test.db"` in a pytest fixture.
No class instantiation needed — module-level global is sufficient for test isolation.

```python
@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr("feedy.storage.DB_PATH", tmp_path / "test.db")
```

---

## Out of Scope (Day 03)

- Filtering by source or date range (CLI, Day 10)
- Schema migrations
- Pagination of `all_entries()`
- Multi-process / concurrent write safety
