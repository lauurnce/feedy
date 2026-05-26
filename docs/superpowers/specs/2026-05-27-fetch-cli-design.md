# Design: `feedy fetch` CLI Command (Day 09)

## Overview

Implement the `feedy fetch` Click command so it runs all configured sources, saves new entries to SQLite, and prints a per-source summary.

## Scope

- Modify `feedy/cli.py` — replace the `fetch()` stub with a real implementation
- Add tests in `tests/test_cli.py`

## Implementation

### Source list

Hardcoded in `cli.py`:

```python
SOURCES = [TelegramSource(), TikTokSource(), MetaSource(), HackerNewsSource()]
```

No config file, no CLI flags. Day 16 will introduce config-driven source selection.

### Fetch loop

```
for each source in SOURCES:
    try:
        entries = source.run()
        saved, skipped = storage.save_many(entries)
        print f"[{source.name}] {saved} new, {skipped} skipped"
    except Exception as e:
        print f"[{source.name}] error: {e}"
```

`source.run()` already handles HTTP errors internally (returns `[]`). The outer `try/except` catches anything unexpected without killing subsequent sources.

### Output format

```
[telegram] 12 new, 3 skipped
[tiktok] 0 new, 0 skipped
[meta] 8 new, 1 skipped
[hackernews] 15 new, 5 skipped
---
Total: 35 new entries saved.
```

Total counts only `saved` across all sources.

## Error handling

- HTTP fetch failures: already handled inside each source's `fetch()` — returns `[]`, no entries saved
- Unexpected exceptions per source: caught, printed, loop continues
- No exit codes changed — CLI exits 0 regardless (fetch is best-effort)

## Tests

File: `tests/test_cli.py`

Use Click's `CliRunner` to invoke `feedy fetch`. Mock `source.run()` per source and `storage.save_many()`. Assert:
- Each source's `run()` called exactly once
- `save_many()` called with correct entries per source
- Output contains per-source summary lines
- Output contains correct total

## Out of scope

- Selecting specific sources via CLI args (Day 16)
- Progress indicators or verbose mode
- `feedy list` command (Day 10)
