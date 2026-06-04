# MetaSource Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `MetaSource` that scrapes blog post titles, URLs, and dates from `developers.facebook.com/blog`.

**Architecture:** `httpx` fetches static HTML; `BeautifulSoup` selects `a[href*="/blog/post/"]` cards and extracts `h3` titles, `h6` dates, and `href` URLs. Date strings like `"APRIL 14, 2026"` are normalized to ISO 8601.

**Tech Stack:** Python 3.11+, `httpx`, `beautifulsoup4`, `pytest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `feedy/sources/meta.py` | MetaSource class + `_parse_date` helper |
| Create | `tests/test_meta.py` | All unit tests for MetaSource |

---

### Task 1: Module skeleton + name test

**Files:**
- Create: `feedy/sources/meta.py`
- Create: `tests/test_meta.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_meta.py`:

```python
import pytest
from feedy.sources.meta import MetaSource


@pytest.fixture
def source():
    return MetaSource()


def test_source_name(source):
    assert source.name == "meta"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_meta.py::test_source_name -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'feedy.sources.meta'`

- [ ] **Step 3: Write minimal implementation**

Create `feedy/sources/meta.py`:

```python
from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://developers.facebook.com"
_BLOG_URL = f"{_BASE_URL}/blog/"
_CARD_SELECTOR = 'a[href*="/blog/post/"]'


class MetaSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "meta"

    def fetch(self) -> list:
        try:
            response = httpx.get(
                _BLOG_URL,
                timeout=10,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[MetaSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        return []

    def to_dict(self, entry: dict) -> FeedEntry:
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/test_meta.py::test_source_name -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```
git add feedy/sources/meta.py tests/test_meta.py
git commit -m "feat(meta): skeleton MetaSource, name test passes"
```

---

### Task 2: parse() — happy path (title, URL, date)

**Files:**
- Modify: `feedy/sources/meta.py` — implement `parse()` and `_parse_date()`
- Modify: `tests/test_meta.py` — add happy-path tests

- [ ] **Step 1: Add HTML fixture and happy-path tests**

Append to `tests/test_meta.py`:

```python
import textwrap

_TWO_CARDS_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/blog/post/2026/04/14/threads-api/">
        <h6>APRIL 14, 2026</h6>
        <h3>What's new in the Threads API</h3>
    </a>
    <a href="/blog/post/2026/03/25/marketing-api/">
        <h6>MARCH 25, 2026</h6>
        <h3>Marketing API Updates</h3>
    </a>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert len(result) == 2


def test_parse_extracts_title(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["title"] == "What's new in the Threads API"
    assert result[1]["title"] == "Marketing API Updates"


def test_parse_expands_relative_url(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["url"] == "https://developers.facebook.com/blog/post/2026/04/14/threads-api/"
    assert result[1]["url"] == "https://developers.facebook.com/blog/post/2026/03/25/marketing-api/"


def test_parse_parses_date_to_iso(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["date"] == "2026-04-14"
    assert result[1]["date"] == "2026-03-25"
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_meta.py -k "happy or title or url or date or entries" -v
```

Expected: all 4 new tests `FAILED`

- [ ] **Step 3: Implement parse() and _parse_date()**

Replace the stub `parse()` and add `_parse_date()` at the bottom of `feedy/sources/meta.py`:

```python
    def parse(self, raw: list) -> list[dict]:
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        cards = soup.select(_CARD_SELECTOR)
        results = []
        for card in cards:
            href = card.get("href", "")
            if href.startswith("/"):
                href = f"{_BASE_URL}{href}"
            if not href:
                continue
            title_el = card.select_one("h3")
            if not title_el:
                continue
            date_el = card.select_one("h6")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": href,
                "date": _parse_date(date_el.get_text(strip=True) if date_el else ""),
            })
        return results


def _parse_date(raw: str) -> str:
    try:
        return datetime.strptime(raw.title(), "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_meta.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 5: Commit**

```
git add feedy/sources/meta.py tests/test_meta.py
git commit -m "feat(meta): implement parse() with title, URL, date extraction"
```

---

### Task 3: parse() — edge cases

**Files:**
- Modify: `tests/test_meta.py` — add edge-case tests (no title, empty input, absolute URL, missing date)

- [ ] **Step 1: Add edge-case fixtures and tests**

Append to `tests/test_meta.py`:

```python
_NO_TITLE_CARD_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/blog/post/2026/01/01/no-title/">
        <h6>JANUARY 1, 2026</h6>
    </a>
    </body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <a href="https://developers.facebook.com/blog/post/2026/01/01/absolute/">
        <h6>JANUARY 1, 2026</h6>
        <h3>Absolute URL Post</h3>
    </a>
    </body></html>
""")

_NO_DATE_CARD_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/blog/post/2026/01/01/no-date/">
        <h3>No Date Post</h3>
    </a>
    </body></html>
""")


def test_parse_skips_card_with_no_title(source):
    result = source.parse([_NO_TITLE_CARD_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_preserves_absolute_url(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://developers.facebook.com/blog/post/2026/01/01/absolute/"


def test_parse_empty_date_on_missing_h6(source):
    result = source.parse([_NO_DATE_CARD_HTML])
    assert result[0]["date"] == ""
```

- [ ] **Step 2: Run edge-case tests to verify they pass (no new implementation needed)**

```
pytest tests/test_meta.py -v
```

Expected: all tests `PASSED` — existing `parse()` already handles these cases.

- [ ] **Step 3: Commit**

```
git add tests/test_meta.py
git commit -m "test(meta): add edge case tests for parse()"
```

---

### Task 4: to_dict() and run()

**Files:**
- Modify: `tests/test_meta.py` — add to_dict and run tests

- [ ] **Step 1: Add to_dict and run tests**

Append to `tests/test_meta.py`:

```python
def test_to_dict_sets_source_to_meta(source):
    entry = {"url": "https://developers.facebook.com/blog/post/x/", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["source"] == "meta"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://developers.facebook.com/blog/post/x/", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://developers.facebook.com/blog/post/x/", "title": "Post Title", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["url"] == "https://developers.facebook.com/blog/post/x/"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_CARD_HTML])
    result = source.run()
    assert result == []
```

- [ ] **Step 2: Run tests to verify they pass**

```
pytest tests/test_meta.py -v
```

Expected: all tests `PASSED` — `to_dict()` and `run()` already implemented in skeleton.

- [ ] **Step 3: Run full test suite to verify no regressions**

```
pytest -v
```

Expected: all tests `PASSED`

- [ ] **Step 4: Commit**

```
git add tests/test_meta.py
git commit -m "test(meta): add to_dict and run tests"
```

---

### Task 5: Mark Day 08 complete

**Files:**
- Modify: `roadmap.md`

- [ ] **Step 1: Mark Day 08 done in roadmap**

In `roadmap.md`, change:

```
- [ ] Day 08 — MetaSource: scrape developers.facebook.com/blog
```

to:

```
- [x] Day 08 — MetaSource: scrape developers.facebook.com/blog
```

- [ ] **Step 2: Commit**

```
git add roadmap.md
git commit -m "chore: mark Day 08 complete"
```
