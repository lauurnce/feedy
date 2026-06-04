# Design: `feedy digest` CLI Command (Day 14)

## Overview

Wire up the `feedy digest` Click command stub to load entries from storage, run them through the AI summarizer, persist new summaries back to the DB, and print the formatted digest.

## Scope

- Modify `feedy/cli.py` — replace the `digest()` stub with real implementation; import `summarize` and `build_digest`
- Add tests in `tests/test_cli.py`
- Modify `roadmap.md` — mark Day 14 complete

## Interface

```
feedy digest [--since DATE] [--source NAME]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--since` | today's date (`YYYY-MM-DD`) | Load entries on or after this date |
| `--source` | none (all sources) | Filter by source name |

## Data Flow

```
digest(since, source)
  → if since is None: since = today
  → entries = storage.get_entries(source=source, since=since)
  → if no entries: echo "No entries found." and return
  → summarized = summarize(entries)          # AI call; skips already-summarized
  → for each entry where summary changed: storage.update_summary(url, summary)
  → click.echo(build_digest(summarized))
```

## Output Example

```
## Hackernews
• New AI SDK Release — Adds streaming support and cuts latency by 40%.
• GraphQL Breaking Change — Removes deprecated fields; migration guide linked.

## Telegram
• Telegram 10.2 — Introduces Stories API for bots.
```

No entries case:
```
No entries found.
```

## Dependencies

| Symbol | Source |
|--------|--------|
| `storage` | `import feedy.storage as storage` (already in cli.py) |
| `summarize` | `from feedy.summarizer import summarize` |
| `build_digest` | `from feedy.digest import build_digest` |

## Why Persist Summaries

`summarize()` skips entries where `entry["summary"]` is already set. Without persisting, every `feedy digest` run makes fresh API calls for every entry. Calling `storage.update_summary()` after summarization means subsequent runs are instant for already-processed entries.

## Error Handling

| Case | Behaviour |
|------|-----------|
| No entries found | Print `"No entries found."`, exit 0 |
| `ANTHROPIC_API_KEY` missing | `summarize()` returns entries with `summary=""`, digest prints titles only |
| `summarize()` raises | Propagates (no special handling needed at CLI layer) |

## Out of Scope

- `--no-ai` flag (Day 15)
- Markdown export (Day 17)
- Per-entry date output in digest
