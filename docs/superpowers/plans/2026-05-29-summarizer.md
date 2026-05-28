# Summarizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `feedy/summarizer.py` with a `summarize(entries)` function that generates 2-sentence AI summaries for unsummarized feed entries using `feedy.ai.complete`.

**Architecture:** Single module with one public function and one private prompt builder. Depends only on `feedy.ai.complete` — no storage, no side effects. Returns a new list of dicts with `summary` populated; originals are never mutated. Entries that already have a non-empty summary are copied unchanged.

**Tech Stack:** Python 3.11+, `feedy.ai.complete` (Day 11), `unittest.mock`, `pytest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `feedy/summarizer.py` | `summarize()` + `_build_prompt()` |
| Create | `tests/test_summarizer.py` | 6 unit tests |
| Modify | `roadmap.md` | Mark Day 12 complete |

---

### Task 1: Failing tests for `summarize()`

**Files:**
- Create: `tests/test_summarizer.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_summarizer.py` with this content:

```python
from unittest.mock import patch

import pytest

from feedy.summarizer import summarize


_ENTRY = {
    "url": "https://example.com/post",
    "title": "Example Post",
    "date": "2026-05-29",
    "source": "telegram",
    "summary": "",
}


def test_summarize_calls_complete_for_unsummarized_entry():
    entry = {**_ENTRY, "summary": ""}
    with patch("feedy.summarizer.complete", return_value="Two sentence summary.") as mock_complete:
        result = summarize([entry])
    mock_complete.assert_called_once()
    assert result[0]["summary"] == "Two sentence summary."


def test_summarize_skips_already_summarized_entry():
    entry = {**_ENTRY, "summary": "Already summarized."}
    with patch("feedy.summarizer.complete") as mock_complete:
        result = summarize([entry])
    mock_complete.assert_not_called()
    assert result[0]["summary"] == "Already summarized."


def test_summarize_sets_empty_summary_when_complete_returns_none():
    entry = {**_ENTRY, "summary": ""}
    with patch("feedy.summarizer.complete", return_value=None):
        result = summarize([entry])
    assert result[0]["summary"] == ""


def test_summarize_empty_input_returns_empty_list():
    result = summarize([])
    assert result == []


def test_summarize_does_not_mutate_input():
    entry = {**_ENTRY, "summary": ""}
    with patch("feedy.summarizer.complete", return_value="New summary."):
        summarize([entry])
    assert entry["summary"] == ""


def test_summarize_prompt_contains_title_url_source():
    entry = {**_ENTRY}
    with patch("feedy.summarizer.complete", return_value="Summary.") as mock_complete:
        summarize([entry])
    prompt = mock_complete.call_args[0][0]
    assert entry["title"] in prompt
    assert entry["url"] in prompt
    assert entry["source"] in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

```
.venv\Scripts\pytest.exe tests/test_summarizer.py -v
```

Expected: all 6 fail with `ModuleNotFoundError: No module named 'feedy.summarizer'`

- [ ] **Step 3: Commit**

```
git add tests/test_summarizer.py
git commit -m "test(summarizer): add failing tests for summarize()"
```

---

### Task 2: Implement `feedy/summarizer.py`

**Files:**
- Create: `feedy/summarizer.py`

- [ ] **Step 1: Write the implementation**

Create `feedy/summarizer.py` with this content:

```python
from __future__ import annotations

from feedy.ai import complete
from feedy.sources.base import FeedEntry


def summarize(entries: list[FeedEntry]) -> list[FeedEntry]:
    """Return new list of entries with summary populated via AI. Skips already-summarized."""
    results = []
    for entry in entries:
        if entry["summary"]:
            results.append(dict(entry))
        else:
            summary = complete(_build_prompt(entry)) or ""
            results.append({**entry, "summary": summary})
    return results


def _build_prompt(entry: FeedEntry) -> str:
    return (
        "Summarize this developer blog post in exactly 2 sentences.\n"
        f"Title: {entry['title']}\n"
        f"URL: {entry['url']}\n"
        f"Source: {entry['source']}\n\n"
        "Focus on what changed or was announced and why it matters to developers."
    )
```

- [ ] **Step 2: Run `test_summarizer.py` to verify all 6 pass**

```
.venv\Scripts\pytest.exe tests/test_summarizer.py -v
```

Expected:
```
tests/test_summarizer.py::test_summarize_calls_complete_for_unsummarized_entry PASSED
tests/test_summarizer.py::test_summarize_skips_already_summarized_entry PASSED
tests/test_summarizer.py::test_summarize_sets_empty_summary_when_complete_returns_none PASSED
tests/test_summarizer.py::test_summarize_empty_input_returns_empty_list PASSED
tests/test_summarizer.py::test_summarize_does_not_mutate_input PASSED
tests/test_summarizer.py::test_summarize_prompt_contains_title_url_source PASSED

6 passed
```

- [ ] **Step 3: Run full test suite to check for regressions**

```
.venv\Scripts\pytest.exe -v
```

Expected: all existing tests pass (was 86 after Task 1 commit, now 92 total).

- [ ] **Step 4: Commit**

```
git add feedy/summarizer.py
git commit -m "feat(summarizer): add summarize() with 2-sentence AI summary per entry"
```

---

### Task 3: Mark Day 12 complete

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Update roadmap**

In `ROADMAP.md`, change:

```
- [ ] Day 12 — Summarizer: takes raw entries, returns 2-sentence AI summary per item
```

to:

```
- [x] Day 12 — Summarizer: takes raw entries, returns 2-sentence AI summary per item
```

- [ ] **Step 2: Commit**

```
git add ROADMAP.md
git commit -m "chore: mark Day 12 complete"
```
