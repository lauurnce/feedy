# Digest Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `feedy/digest.py` with `build_digest(entries)` that groups feed entries by source and returns a formatted multi-section digest string.

**Architecture:** Single pure function — takes `list[FeedEntry]`, groups by `source` key, sorts groups alphabetically, formats each as `## Source\n• Title — Summary\n`, joins sections with a blank line. No I/O, no AI calls, no storage dependency.

**Tech Stack:** Python 3.11+ stdlib only (`collections.defaultdict`), `pytest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `feedy/digest.py` | `build_digest()` function |
| Create | `tests/test_digest.py` | 6 unit tests |
| Modify | `ROADMAP.md` | Mark Day 13 complete |

---

### Task 1: Failing tests for `build_digest()`

**Files:**
- Create: `tests/test_digest.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_digest.py` with this content:

```python
from feedy.digest import build_digest


def test_single_entry_with_summary():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Great summary here."}]
    result = build_digest(entries)
    assert "• My Post — Great summary here." in result


def test_single_entry_without_summary():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": ""}]
    result = build_digest(entries)
    assert "• My Post" in result
    assert " — " not in result


def test_multiple_sources_sorted_alphabetically():
    entries = [
        {"url": "https://ex.com/1", "title": "Post 1", "date": "2026-05-29", "source": "telegram", "summary": "Sum 1."},
        {"url": "https://ex.com/2", "title": "Post 2", "date": "2026-05-29", "source": "hackernews", "summary": "Sum 2."},
    ]
    result = build_digest(entries)
    assert result.index("## Hackernews") < result.index("## Telegram")


def test_empty_input_returns_empty_string():
    assert build_digest([]) == ""


def test_source_header_capitalized():
    entries = [{"url": "https://ex.com", "title": "Post", "date": "2026-05-29", "source": "hackernews", "summary": "Sum."}]
    result = build_digest(entries)
    assert "## Hackernews" in result


def test_groups_separated_by_blank_line():
    entries = [
        {"url": "https://ex.com/1", "title": "Post 1", "date": "2026-05-29", "source": "telegram", "summary": "Sum 1."},
        {"url": "https://ex.com/2", "title": "Post 2", "date": "2026-05-29", "source": "meta", "summary": "Sum 2."},
    ]
    result = build_digest(entries)
    assert "\n\n" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```
.venv\Scripts\pytest.exe tests/test_digest.py -v
```

Expected: all 6 fail with `ModuleNotFoundError: No module named 'feedy.digest'`

- [ ] **Step 3: Commit**

```
git add tests/test_digest.py
git commit -m "test(digest): add failing tests for build_digest()"
```

---

### Task 2: Implement `feedy/digest.py`

**Files:**
- Create: `feedy/digest.py`

- [ ] **Step 1: Write the implementation**

Create `feedy/digest.py` with this content:

```python
from __future__ import annotations

from collections import defaultdict

from feedy.sources.base import FeedEntry


def build_digest(entries: list[FeedEntry]) -> str:
    """Group entries by source and format as a readable digest string."""
    if not entries:
        return ""

    groups: dict[str, list[FeedEntry]] = defaultdict(list)
    for entry in entries:
        groups[entry["source"]].append(entry)

    sections = []
    for source in sorted(groups):
        lines = [f"## {source.capitalize()}"]
        for entry in groups[source]:
            if entry["summary"]:
                lines.append(f"• {entry['title']} — {entry['summary']}")
            else:
                lines.append(f"• {entry['title']}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
```

- [ ] **Step 2: Run `test_digest.py` to verify all 6 pass**

```
.venv\Scripts\pytest.exe tests/test_digest.py -v
```

Expected:
```
tests/test_digest.py::test_single_entry_with_summary PASSED
tests/test_digest.py::test_single_entry_without_summary PASSED
tests/test_digest.py::test_multiple_sources_sorted_alphabetically PASSED
tests/test_digest.py::test_empty_input_returns_empty_string PASSED
tests/test_digest.py::test_source_header_capitalized PASSED
tests/test_digest.py::test_groups_separated_by_blank_line PASSED

6 passed
```

- [ ] **Step 3: Run full test suite to check for regressions**

```
.venv\Scripts\pytest.exe -v
```

Expected: all 98 tests pass (92 existing + 6 new).

- [ ] **Step 4: Commit**

```
git add feedy/digest.py
git commit -m "feat(digest): add build_digest() grouping entries by source"
```

---

### Task 3: Mark Day 13 complete

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Update roadmap**

In `ROADMAP.md`, change:

```
- [ ] Day 13 — Digest builder: groups entries by platform, formats into readable digest
```

to:

```
- [x] Day 13 — Digest builder: groups entries by platform, formats into readable digest
```

- [ ] **Step 2: Commit**

```
git add ROADMAP.md
git commit -m "chore: mark Day 13 complete"
```
