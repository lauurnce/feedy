# SQLite Storage Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `feedy/storage.py` with lazy DB init, batch save, and summary update — all test-driven.

**Architecture:** Single module of module-level functions backed by SQLite stdlib. `_connect()` runs `CREATE TABLE IF NOT EXISTS` on every call (idempotent), eliminating the need for callers to call `init_db()`. Two new public functions added: `save_many()` and `update_summary()`.

**Tech Stack:** Python 3.11+, `sqlite3` (stdlib), `pytest`, `pathlib`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `feedy/storage.py` | Core storage module — all DB logic |
| Create | `tests/test_storage.py` | All storage unit tests |

---

## Task 1: Test infrastructure — isolated DB fixture

**Files:**
- Create: `tests/test_storage.py`

- [ ] **Step 1: Create `tests/test_storage.py` with the isolation fixture**

```python
import pytest
import feedy.storage as storage


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")
```

Note: import the module object (`import feedy.storage as storage`), not individual functions. All tests call `storage.save(...)` etc. This means new functions added in later tasks are always reachable without changing the import line.

- [ ] **Step 2: Run to confirm fixture loads without error**

```
pytest tests/test_storage.py -v
```

Expected: `no tests ran` — no errors, no collected tests yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_storage.py
git commit -m "test: add isolated DB fixture for storage tests"
```

---

## Task 2: Lazy init — `_connect()` creates table automatically

**Files:**
- Modify: `feedy/storage.py` — inline `CREATE TABLE` in `_connect()`, update `init_db()`
- Modify: `tests/test_storage.py` — add failing test

- [ ] **Step 1: Write the failing test**

Add to `tests/test_storage.py`:

```python
def test_save_works_without_calling_init_db():
    # Must not require explicit init_db() call first
    result = storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-17", "source": "x", "summary": ""})
    assert result is True
```

- [ ] **Step 2: Run to verify it fails**

```
pytest tests/test_storage.py::test_save_works_without_calling_init_db -v
```

Expected: FAIL — `OperationalError: no such table: entries`

- [ ] **Step 3: Implement lazy init in `feedy/storage.py`**

Replace the entire file with:

```python
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".feedy" / "feedy.db"

_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS entries (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        url         TEXT UNIQUE NOT NULL,
        title       TEXT,
        date        TEXT,
        source      TEXT,
        summary     TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    )
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE)
    conn.commit()
    return conn


def init_db() -> None:
    """Kept for backward compatibility. Init is now lazy inside _connect()."""
    _connect().close()


def save(entry: dict) -> bool:
    """Insert entry; return False if URL already exists (dedup)."""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO entries (url, title, date, source, summary) VALUES (?, ?, ?, ?, ?)",
                (entry["url"], entry.get("title"), entry.get("date"), entry.get("source"), entry.get("summary")),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def all_entries() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM entries ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/test_storage.py::test_save_works_without_calling_init_db -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add feedy/storage.py tests/test_storage.py
git commit -m "feat: lazy DB init inside _connect()"
```

---

## Task 3: `save()` dedup behaviour

**Files:**
- Modify: `tests/test_storage.py` — add dedup + retrieval tests

- [ ] **Step 1: Write the tests**

Add to `tests/test_storage.py`:

```python
def test_save_returns_true_on_new_entry():
    result = storage.save({"url": "https://b.com", "title": "B", "date": "2026-05-17", "source": "x", "summary": ""})
    assert result is True


def test_save_returns_false_on_duplicate_url():
    entry = {"url": "https://c.com", "title": "C", "date": "2026-05-17", "source": "x", "summary": ""}
    storage.save(entry)
    result = storage.save(entry)
    assert result is False


def test_save_stores_entry_retrievable_via_all_entries():
    storage.save({"url": "https://d.com", "title": "D", "date": "2026-05-17", "source": "x", "summary": ""})
    entries = storage.all_entries()
    assert len(entries) == 1
    assert entries[0]["url"] == "https://d.com"
    assert entries[0]["title"] == "D"
```

- [ ] **Step 2: Run to verify they pass**

```
pytest tests/test_storage.py -v
```

Expected: all PASS — `save()` and `all_entries()` are already implemented.

- [ ] **Step 3: Commit**

```bash
git add tests/test_storage.py
git commit -m "test: verify save() dedup and all_entries() retrieval"
```

---

## Task 4: `save_many()` — batch insert returning `(saved, skipped)`

**Files:**
- Modify: `tests/test_storage.py` — add failing tests
- Modify: `feedy/storage.py` — add `save_many()`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_storage.py`:

```python
def test_save_many_returns_saved_and_skipped_counts():
    entries = [
        {"url": "https://e.com", "title": "E", "date": "2026-05-17", "source": "x", "summary": ""},
        {"url": "https://f.com", "title": "F", "date": "2026-05-17", "source": "x", "summary": ""},
    ]
    saved, skipped = storage.save_many(entries)
    assert saved == 2
    assert skipped == 0


def test_save_many_counts_duplicates_as_skipped():
    entry = {"url": "https://g.com", "title": "G", "date": "2026-05-17", "source": "x", "summary": ""}
    storage.save(entry)  # pre-insert duplicate
    entries = [
        entry,  # duplicate
        {"url": "https://h.com", "title": "H", "date": "2026-05-17", "source": "x", "summary": ""},
    ]
    saved, skipped = storage.save_many(entries)
    assert saved == 1
    assert skipped == 1


def test_save_many_empty_list_returns_zero_zero():
    saved, skipped = storage.save_many([])
    assert saved == 0
    assert skipped == 0
```

- [ ] **Step 2: Run to verify they fail**

```
pytest tests/test_storage.py -k "save_many" -v
```

Expected: FAIL — `AttributeError: module 'feedy.storage' has no attribute 'save_many'`

- [ ] **Step 3: Add `save_many()` to `feedy/storage.py`**

Add this function after `all_entries()`:

```python
def save_many(entries: list[dict]) -> tuple[int, int]:
    saved = skipped = 0
    for entry in entries:
        if save(entry):
            saved += 1
        else:
            skipped += 1
    return saved, skipped
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_storage.py -k "save_many" -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add feedy/storage.py tests/test_storage.py
git commit -m "feat: add save_many() with (saved, skipped) return"
```

---

## Task 5: `update_summary()` — patch summary by URL

**Files:**
- Modify: `tests/test_storage.py` — add failing tests
- Modify: `feedy/storage.py` — add `update_summary()`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_storage.py`:

```python
def test_update_summary_returns_true_when_url_exists():
    storage.save({"url": "https://i.com", "title": "I", "date": "2026-05-17", "source": "x", "summary": ""})
    result = storage.update_summary("https://i.com", "AI wrote this.")
    assert result is True


def test_update_summary_persists_new_summary():
    storage.save({"url": "https://j.com", "title": "J", "date": "2026-05-17", "source": "x", "summary": ""})
    storage.update_summary("https://j.com", "Updated summary.")
    entries = storage.all_entries()
    assert entries[0]["summary"] == "Updated summary."


def test_update_summary_returns_false_when_url_missing():
    result = storage.update_summary("https://notexist.com", "ghost")
    assert result is False
```

- [ ] **Step 2: Run to verify they fail**

```
pytest tests/test_storage.py -k "update_summary" -v
```

Expected: FAIL — `AttributeError: module 'feedy.storage' has no attribute 'update_summary'`

- [ ] **Step 3: Add `update_summary()` to `feedy/storage.py`**

Add after `save_many()`:

```python
def update_summary(url: str, summary: str) -> bool:
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE entries SET summary = ? WHERE url = ?",
            (summary, url),
        )
    return cursor.rowcount > 0
```

- [ ] **Step 4: Run all tests to verify everything passes**

```
pytest tests/test_storage.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add feedy/storage.py tests/test_storage.py
git commit -m "feat: add update_summary() for AI post-processing"
```

---

## Task 6: Full suite + mark Day 03 complete

**Files:**
- Modify: `ROADMAP.md` — mark Day 03 done

- [ ] **Step 1: Run full test suite**

```
pytest -v
```

Expected: all PASS, no collection errors.

- [ ] **Step 2: Mark Day 03 done in `ROADMAP.md`**

Change:
```
- [ ] Day 03 — SQLite storage module with save and dedup by URL
```
To:
```
- [x] Day 03 — SQLite storage module with save and dedup by URL
```

- [ ] **Step 3: Commit**

```bash
git add ROADMAP.md
git commit -m "chore: mark Day 03 complete"
```
