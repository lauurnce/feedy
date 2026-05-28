# Anthropic Client Design

**Date:** 2026-05-29
**Feature:** Day 11 — Anthropic API integration module (client wrapper + error handling)

---

## Architecture

- **File:** `feedy/ai.py`
- **Tests:** `tests/test_ai.py`
- One public function: `complete(prompt: str) -> str | None`
- No class, no state — matches project's flat module style

```
feedy/
  ai.py          ← new
  cli.py
  storage.py
  sources/
    ...
tests/
  test_ai.py     ← new
```

## Interface

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `complete` | `(prompt: str) -> str \| None` | Response text or `None` on any failure |

## Data Flow

```
caller (Day 12 summarizer)
  → complete(prompt)
      → read ANTHROPIC_API_KEY from os.environ
      → if missing or empty: return None
      → client = anthropic.Anthropic(api_key=key)
      → client.messages.create(
             model="claude-haiku-4-5-20251001",
             max_tokens=300,
             messages=[{"role": "user", "content": prompt}]
         )
      → return message.content[0].text.strip()
      → on APIError: return None
      → on empty content list: return None
```

## Configuration

| Parameter | Source | Notes |
|-----------|--------|-------|
| API key | `os.environ["ANTHROPIC_API_KEY"]` | Read at call time, not import time |
| Model | Hardcoded `"claude-haiku-4-5-20251001"` | Fast + cheap for 2-sentence summaries |
| max_tokens | `300` | Sufficient for 2-sentence output |

Key is read at call time (not module load) so tests can set `os.environ` without import-order issues.

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| `ANTHROPIC_API_KEY` unset or empty | Return `None` immediately, no API call |
| `anthropic.APIError` (auth, rate limit, server 5xx) | Catch, return `None` |
| `content` list empty | Return `None` |
| Any other unexpected exception | Propagate — not silenced |

No printing/logging in this module. Callers decide how to surface failures.

## Out of Scope

- Streaming responses
- Multi-turn conversations
- Prompt caching (Day 15 prompt tuning may revisit)
- Retry logic
- Custom exceptions

## Testing (`tests/test_ai.py`)

Five tests, all monkeypatching `anthropic.Anthropic`:

| Test | Assertion |
|------|-----------|
| success path | returns stripped text from `content[0].text` |
| missing env var | returns `None` without constructing client |
| empty env var | returns `None` without constructing client |
| `anthropic.APIError` raised | returns `None` |
| empty `content` list | returns `None` |
