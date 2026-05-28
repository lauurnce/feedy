# Anthropic Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `feedy/ai.py` with a single `complete(prompt)` function that calls the Anthropic API and returns the text response or `None` on any failure.

**Architecture:** Thin module with one public function; reads `ANTHROPIC_API_KEY` from env at call time; constructs an `anthropic.Anthropic` client per call; catches `anthropic.APIError` and empty-content cases silently; all other exceptions propagate.

**Tech Stack:** `anthropic>=0.28` (already in `pyproject.toml`), `pytest`, `unittest.mock`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `feedy/ai.py` | Public `complete()` function + error handling |
| Create | `tests/test_ai.py` | Five unit tests covering all paths |

---

### Task 1: Failing tests for `complete()`

**Files:**
- Create: `tests/test_ai.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ai.py` with this content:

```python
import os
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from feedy.ai import complete


def _mock_client(text: str) -> MagicMock:
    """Build a mock anthropic.Anthropic that returns `text` from messages.create."""
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    client = MagicMock()
    client.messages.create.return_value = msg
    return client


def test_complete_returns_text(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = _mock_client("  hello world  ")
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result == "hello world"


def test_complete_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = complete("say hello")
    assert result is None


def test_complete_empty_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    result = complete("say hello")
    assert result is None


def test_complete_api_error(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.APIError(
        message="rate limited", request=MagicMock(), body=None
    )
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result is None


def test_complete_empty_content(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    msg = MagicMock()
    msg.content = []
    mock_client = MagicMock()
    mock_client.messages.create.return_value = msg
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_ai.py -v
```

Expected: all 5 fail with `ModuleNotFoundError: No module named 'feedy.ai'`

---

### Task 2: Implement `feedy/ai.py`

**Files:**
- Create: `feedy/ai.py`

- [ ] **Step 1: Write the implementation**

Create `feedy/ai.py` with this content:

```python
from __future__ import annotations

import os

import anthropic

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 300


def complete(prompt: str) -> str | None:
    """Call the Anthropic API with prompt; return text or None on any failure."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    client = anthropic.Anthropic(api_key=key)
    try:
        message = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError:
        return None
    if not message.content:
        return None
    return message.content[0].text.strip()
```

- [ ] **Step 2: Run tests to verify they pass**

```
pytest tests/test_ai.py -v
```

Expected output:
```
tests/test_ai.py::test_complete_returns_text PASSED
tests/test_ai.py::test_complete_missing_key PASSED
tests/test_ai.py::test_complete_empty_key PASSED
tests/test_ai.py::test_complete_api_error PASSED
tests/test_ai.py::test_complete_empty_content PASSED

5 passed
```

- [ ] **Step 3: Run the full test suite to check for regressions**

```
pytest -v
```

Expected: all existing tests still pass.

- [ ] **Step 4: Commit**

```
git add feedy/ai.py tests/test_ai.py
git commit -m "feat(ai): add complete() Anthropic client wrapper with error handling"
```

---

### Task 3: Mark Day 11 complete

**Files:**
- Modify: `roadmap.md`

- [ ] **Step 1: Update roadmap**

In `roadmap.md`, change:

```
- [ ] Day 11 — Anthropic API integration module (client wrapper + error handling)
```

to:

```
- [x] Day 11 — Anthropic API integration module (client wrapper + error handling)
```

- [ ] **Step 2: Commit**

```
git add roadmap.md
git commit -m "chore: mark Day 11 complete"
```
