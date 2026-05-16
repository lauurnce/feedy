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
