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
    """Open a Row-factory connection, creating the parent directory and entries table if absent."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE)
    conn.commit()
    return conn


def init_db() -> None:
    """Kept for backward compatibility. Init is now lazy inside _connect()."""
    conn = _connect()
    conn.close()


def save(entry: dict) -> bool:
    """Insert entry; return False if URL already exists (dedup)."""
    conn = _connect()
    try:
        with conn:
            conn.execute(
                "INSERT INTO entries (url, title, date, source, summary) VALUES (?, ?, ?, ?, ?)",
                (entry["url"], entry.get("title"), entry.get("date"), entry.get("source"), entry.get("summary")),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def save_many(entries: list[dict]) -> tuple[int, int]:
    """Insert each entry, returning (saved, skipped) where skipped counts url collisions."""
    saved = skipped = 0
    for entry in entries:
        if save(entry):
            saved += 1
        else:
            skipped += 1
    return saved, skipped


def update_summary(url: str, summary: str) -> bool:
    """Update summary for an entry by URL. Return True if URL exists, False otherwise."""
    conn = _connect()
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE entries SET summary = ? WHERE url = ?",
                (summary, url),
            )
        return cursor.rowcount > 0
    finally:
        conn.close()


def all_entries() -> list[dict]:
    """Return every stored row as a dict, ordered by created_at descending."""
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM entries ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_stats() -> dict[str, int]:
    """Return entry count per source, sorted by source name."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT source, COUNT(*) AS cnt FROM entries GROUP BY source ORDER BY source"
        ).fetchall()
        return {row["source"]: row["cnt"] for row in rows if row["source"]}
    finally:
        conn.close()


def get_entries(source: str | None = None, since: str | None = None) -> list[dict]:
    """Return rows filtered by source and/or minimum date, combined with AND, newest first."""
    conn = _connect()
    try:
        conditions = []
        params: list[str] = []
        if source is not None:
            conditions.append("source = ?")
            params.append(source)
        if since is not None:
            conditions.append("date >= ?")
            params.append(since)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = conn.execute(
            f"SELECT * FROM entries {where} ORDER BY created_at DESC",
            params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
