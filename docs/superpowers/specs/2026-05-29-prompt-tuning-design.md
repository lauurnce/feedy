# Design: Prompt Tuning (Day 15)

**Date:** 2026-05-29
**Feature:** Day 15 — Prompt tuning: improve summary quality, add "why it matters for devs" line

---

## Architecture

- **File:** `feedy/summarizer.py` — only `_build_prompt` changes
- **Tests:** `tests/test_summarizer.py` — add 2 new tests for prompt structure

No interface changes. `summarize()` signature and behavior unchanged — only the text of the prompt it constructs changes.

## Prompt Change

### Before

```
Summarize this developer blog post in exactly 2 sentences.
Title: {title}
URL: {url}
Source: {source}

Focus on what changed or was announced and why it matters to developers.
```

### After

```
Summarize this developer blog post.

Title: {title}
URL: {url}
Source: {source}

Write exactly 3 sentences using this format:
Sentence 1: What was announced or changed.
Sentence 2: The key technical detail or how it works.
Sentence 3: Start with "Why it matters:" followed by the impact for developers.

Example:
Telegram launches Stories API for bots with support for rich media up to 100MB. Developers can create, schedule, and react to story interactions via a REST endpoint with OAuth scoping. Why it matters: Bots can now run announcement campaigns and interactive polls previously limited to human accounts.
```

## Why This Format

- Explicit 3-sentence structure guides the model to cover what/how/why consistently
- "Why it matters:" prefix makes developer impact scannable in the digest
- A concrete example reduces variance in output quality

## Output in Digest

The `summary` field stores the full 3-sentence string. The digest renders it as:

```
## Telegram
• Telegram Bot Update — Telegram launches Stories API for bots with support for rich media up to 100MB. Developers can create, schedule, and react to story interactions via REST. Why it matters: Bots can now run announcement campaigns previously limited to human accounts.
```

## Testing

New tests added to `tests/test_summarizer.py`:

| Test | Assertion |
|------|-----------|
| Prompt instructs "Why it matters:" | `"Why it matters:"` in prompt |
| Prompt requests 3 sentences | `"3 sentences"` in prompt |

Existing tests unaffected (title/url/source still in prompt; all other behavior unchanged).
