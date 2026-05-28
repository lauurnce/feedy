# Digest Builder Design

**Date:** 2026-05-29
**Feature:** Day 13 — Digest builder: groups entries by platform, formats into readable digest

---

## Architecture

- **File:** `feedy/digest.py`
- **Tests:** `tests/test_digest.py`
- One public function: `build_digest(entries: list[FeedEntry]) -> str`
- Pure function — no I/O, no storage, no AI calls

```
feedy/
  ai.py
  summarizer.py
  digest.py        ← new
  cli.py
  storage.py
tests/
  test_digest.py   ← new
```

## Interface

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `build_digest` | `(entries: list[FeedEntry]) -> str` | Formatted digest string, `""` if no entries |

## Data Flow

```
build_digest(entries)
  → if empty: return ""
  → group entries by entry["source"]
  → sort groups alphabetically by source name
  → for each source group:
      append "## {source.capitalize()}\n"
      for each entry in group:
        if entry["summary"]:
          append "• {title} — {summary}\n"
        else:
          append "• {title}\n"
  → join groups with "\n"
  → return stripped string
```

## Output Format Example

```
## Hackernews
• Some Post Title — Two sentence summary here.
• Another Post — Summary of what changed.

## Telegram
• Telegram Blog Update — What this release means for developers.
• Old Post With No Summary
```

## Error Handling

| Case | Behaviour |
|------|-----------|
| Empty `entries` list | Return `""` |
| Entry with `summary=""` | Render as `• Title` (no dash, no summary) |
| Entry with `summary` set | Render as `• Title — Summary` |
| Multiple sources | Each gets its own `## Header`, sorted alphabetically |

No exceptions raised. All inputs produce valid output.

## Out of Scope

- Date filtering (caller's responsibility)
- Entry count limits per source
- URL inclusion in output
- Markdown file writing (Day 17)

## Testing (`tests/test_digest.py`)

| Test | Assertion |
|------|-----------|
| Single entry with summary | Output contains `• Title — Summary` |
| Single entry without summary | Output contains `• Title`, no dash |
| Multiple sources | Two `##` headers present, sorted alphabetically |
| Empty input | Returns `""` |
| Source header capitalized | `hackernews` → `## Hackernews` |
| Groups separated by blank line | `\n\n` between source sections |
