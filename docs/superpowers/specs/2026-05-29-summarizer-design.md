# Summarizer Design

**Date:** 2026-05-29
**Feature:** Day 12 — Summarizer: takes raw entries, returns 2-sentence AI summary per item

---

## Architecture

- **File:** `feedy/summarizer.py`
- **Tests:** `tests/test_summarizer.py`
- One public function: `summarize(entries: list[FeedEntry]) -> list[FeedEntry]`
- Depends on `feedy.ai.complete` — no direct storage dependency

```
feedy/
  ai.py             ← Day 11, unchanged
  summarizer.py     ← new
  cli.py
  storage.py
  sources/
tests/
  test_summarizer.py  ← new
```

## Interface

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `summarize` | `(entries: list[FeedEntry]) -> list[FeedEntry]` | New list with `summary` field populated |

## Data Flow

```
summarize(entries)
  for each entry:
    if entry["summary"] != "":
      copy as-is (already summarized)
    else:
      prompt = _build_prompt(entry)
      result = ai.complete(prompt)
      summary = result if result is not None else ""
      append {**entry, "summary": summary}
  return new list
```

Original dicts are never mutated. Returns a new list of dicts.

## Prompt Template

```
Summarize this developer blog post in exactly 2 sentences.
Title: {title}
URL: {url}
Source: {source}

Focus on what changed or was announced and why it matters to developers.
```

Built by private `_build_prompt(entry: FeedEntry) -> str`.

## Error Handling

| Case | Behaviour |
|------|-----------|
| `ai.complete()` returns `None` | `summary=""`, entry still included in output |
| Entry already has non-empty `summary` | Copied unchanged, no API call |
| Empty `entries` input | Returns `[]` |

No exceptions raised by this module. All failures produce `summary=""`.

## Out of Scope

- Batching / parallel API calls
- Rate limiting / retry logic
- Persisting summaries to DB (caller's responsibility)
- Truncating long titles/URLs before prompting

## Testing (`tests/test_summarizer.py`)

| Test | Assertion |
|------|-----------|
| Single unsummarized entry | `ai.complete` called once, summary in output |
| Already-summarized entry | `ai.complete` not called, original summary preserved |
| `ai.complete` returns `None` | Output entry has `summary=""` |
| Empty input | Returns `[]` |
| Original dicts unchanged | Input list entries unmodified after call |
| Prompt contains title, url, source | Assert all three appear in prompt passed to `complete` |
