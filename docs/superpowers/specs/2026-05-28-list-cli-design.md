# feedy list CLI Design

**Date:** 2026-05-28
**Status:** Approved

## Overview

Implement `feedy list` to display saved entries from the SQLite database in a fixed-width terminal table, with optional filtering by source name and date.

## Architecture

Two files change:

- `feedy/storage.py` — add `get_entries(source=None, since=None)` alongside existing `all_entries()`
- `feedy/cli.py` — replace `list_entries()` stub with real implementation

No new dependencies.

## Components

### `storage.get_entries(source=None, since=None) -> list[dict]`

Builds a parameterized `SELECT * FROM entries` with optional `WHERE` clauses:

- `source` → `source = ?` exact match
- `since` → `date >= ?` on the ISO 8601 date column

Both filters are independent and combinable. Returns rows ordered `created_at DESC`, same shape as `all_entries()`. `all_entries()` is kept unchanged for backward compatibility.

### `feedy list` CLI command

Options:
- `--source TEXT` — filter by source name (optional)
- `--since TEXT` — filter entries on or after date in `YYYY-MM-DD` format (optional); Click `BadParameter` raised if format is invalid

Output: fixed-width table using `str.ljust()` with columns:

```
ID   SOURCE       DATE        TITLE                                          URL
1    hackernews   2026-05-27  Show HN: I built a feed aggregator             https://...
2    telegram     2026-05-26  Telegram Blog: New Features                    https://...
```

- Title truncated to 45 characters
- Empty result (no entries or no matches) prints `"No entries found."` and exits 0

## Data Flow

```
feedy list [--source X] [--since YYYY-MM-DD]
  → validate --since format (if provided) → BadParameter on failure
  → storage.get_entries(source, since)
  → SELECT * FROM entries [WHERE source=? AND date>=?] ORDER BY created_at DESC
  → print header + rows, or "No entries found."
```

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| `--since` not `YYYY-MM-DD` | `click.BadParameter`, exit non-zero, message: `"use YYYY-MM-DD format"` |
| No matching entries | Print `"No entries found."`, exit 0 |
| DB file missing (first run) | `_connect()` creates it; returns empty result |

## Testing

### `tests/test_storage.py` additions

- `test_get_entries_no_filter` — returns all rows when no filters given
- `test_get_entries_filter_source` — only rows matching source returned
- `test_get_entries_filter_since` — only rows with `date >= since` returned
- `test_get_entries_both_filters` — combined source + since filter works
- `test_get_entries_empty_db` — returns `[]` on empty database

### `tests/test_cli.py` additions

- `test_list_prints_table_header` — output contains `ID`, `SOURCE`, `DATE`, `TITLE`, `URL`
- `test_list_shows_entries` — mocked `get_entries` returns 2 rows, both appear in output
- `test_list_no_entries` — empty result → `"No entries found."`
- `test_list_filter_by_source` — `--source hackernews` passes correct arg to `get_entries`
- `test_list_filter_by_since` — `--since 2026-05-01` passes correct arg to `get_entries`
- `test_list_invalid_since` — `--since bad-date` exits non-zero with error message

## Out of Scope

- Pagination (`--page`, `--offset`)
- `--limit N` option
- Sorting by column other than `created_at`
- Coloured terminal output
