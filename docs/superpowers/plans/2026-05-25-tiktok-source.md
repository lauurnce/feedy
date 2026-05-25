# TikTokSource Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `TikTokSource` that scrapes `developers.tiktok.com/blogs` and returns normalized `FeedEntry` objects.

**Architecture:** Single file `feedy/sources/tiktok.py` mirrors `HackerNewsSource` — `fetch()` GETs the listing page, `parse()` selects cards via `data-e2e` attributes with BeautifulSoup, `to_dict()` normalizes to `FeedEntry`. Date field is empty string (not available on site). Tests use offline HTML fixtures, no network.

**Tech Stack:** Python 3.11+, httpx, beautifulsoup4, pytest

---

## File Map

| Action | Path |
|--------|------|
| Create | `feedy/sources/tiktok.py` |
| Create | `tests/test_tiktok.py` |
| Modify | `roadmap.md` — mark Day 07 complete |

---

### Task 1: Source skeleton + name property test

**Files:**
- Create: `feedy/sources/tiktok.py`
- Create: `tests/test_tiktok.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tiktok.py
import pytest
from feedy.sources.tiktok import TikTokSource


@pytest.fixture
def source():
    return TikTokSource()


def test_source_name(source):
    assert source.name == "tiktok"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_tiktok.py::test_source_name -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `tiktok` module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
# feedy/sources/tiktok.py
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://developers.tiktok.com"
_BLOG_URL = f"{_BASE_URL}/blogs"
_CARD_SELECTOR = 'a[data-e2e="CardContainer"]'
_TITLE_SELECTOR = 'span[data-e2e="TUXText"]'


class TikTokSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "tiktok"

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
            print(f"[TikTokSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        raise NotImplementedError

    def to_dict(self, entry: dict) -> FeedEntry:
        raise NotImplementedError
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/test_tiktok.py::test_source_name -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```
git add feedy/sources/tiktok.py tests/test_tiktok.py
git commit -m "feat(tiktok): scaffold TikTokSource with name property"
```

---

### Task 2: parse() — happy path with two cards

**Files:**
- Modify: `feedy/sources/tiktok.py`
- Modify: `tests/test_tiktok.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_tiktok.py`:

```python
import textwrap

_TWO_CARDS_HTML = textwrap.dedent("""\
    <html><body>
    <a data-e2e="CardContainer" href="/blog/first-post">
        <span data-e2e="TUXText">First Post Title</span>
        <span data-e2e="TUXText">Description of first post.</span>
    </a>
    <a data-e2e="CardContainer" href="/blog/second-post">
        <span data-e2e="TUXText">Second Post Title</span>
        <span data-e2e="TUXText">Description of second post.</span>
    </a>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert len(result) == 2


def test_parse_extracts_title_from_first_tux_text(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["title"] == "First Post Title"
    assert result[1]["title"] == "Second Post Title"


def test_parse_expands_relative_url(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["url"] == "https://developers.tiktok.com/blog/first-post"
    assert result[1]["url"] == "https://developers.tiktok.com/blog/second-post"


def test_parse_sets_empty_date(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["date"] == ""
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_tiktok.py -v -k "parse"
```

Expected: `NotImplementedError` for all four tests.

- [ ] **Step 3: Implement parse()**

Replace `raise NotImplementedError` in `parse()`:

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
        title_el = card.select_one(_TITLE_SELECTOR)
        if not title_el:
            continue
        results.append({
            "title": title_el.get_text(strip=True),
            "url": href,
            "date": "",
        })
    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_tiktok.py -v -k "parse"
```

Expected: all 4 `PASSED`

- [ ] **Step 5: Commit**

```
git add feedy/sources/tiktok.py tests/test_tiktok.py
git commit -m "feat(tiktok): implement parse() with data-e2e selectors"
```

---

### Task 3: parse() — edge cases

**Files:**
- Modify: `tests/test_tiktok.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_tiktok.py`:

```python
_NO_TITLE_CARD_HTML = textwrap.dedent("""\
    <html><body>
    <a data-e2e="CardContainer" href="/blog/no-title">
    </a>
    </body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <a data-e2e="CardContainer" href="https://developers.tiktok.com/blog/absolute">
        <span data-e2e="TUXText">Absolute URL Post</span>
    </a>
    </body></html>
""")


def test_parse_skips_card_with_no_title(source):
    result = source.parse([_NO_TITLE_CARD_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_preserves_absolute_url_unchanged(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://developers.tiktok.com/blog/absolute"
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_tiktok.py::test_parse_skips_card_with_no_title tests/test_tiktok.py::test_parse_returns_empty_for_empty_input tests/test_tiktok.py::test_parse_preserves_absolute_url_unchanged -v
```

Expected: `FAILED` — absolute URL test will fail (double-prepend bug not yet handled) and no-title/empty may pass or fail.

- [ ] **Step 3: Fix absolute URL handling in parse()**

The current `if href.startswith("/")` already handles this correctly — absolute URLs are preserved. Verify by running the tests. If `test_parse_preserves_absolute_url_unchanged` still fails, the condition needs adjustment:

```python
if href.startswith("/"):
    href = f"{_BASE_URL}{href}"
# else: href is already absolute, leave unchanged
```

No change needed if the condition already handles it. Run tests to confirm.

- [ ] **Step 4: Run tests to verify they all pass**

```
pytest tests/test_tiktok.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 5: Commit**

```
git add tests/test_tiktok.py
git commit -m "test(tiktok): add edge case tests for parse()"
```

---

### Task 4: to_dict() and run() integration

**Files:**
- Modify: `feedy/sources/tiktok.py`
- Modify: `tests/test_tiktok.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_tiktok.py`:

```python
def test_to_dict_sets_source_to_tiktok(source):
    entry = {"url": "https://developers.tiktok.com/blog/x", "title": "X", "date": ""}
    result = source.to_dict(entry)
    assert result["source"] == "tiktok"


def test_to_dict_sets_empty_date_and_summary(source):
    entry = {"url": "https://developers.tiktok.com/blog/x", "title": "X", "date": ""}
    result = source.to_dict(entry)
    assert result["date"] == ""
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://developers.tiktok.com/blog/x", "title": "Post Title", "date": ""}
    result = source.to_dict(entry)
    assert result["url"] == "https://developers.tiktok.com/blog/x"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_CARD_HTML])
    result = source.run()
    assert result == []
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_tiktok.py -v -k "to_dict or run"
```

Expected: `NotImplementedError` for `to_dict` tests.

- [ ] **Step 3: Implement to_dict()**

Replace `raise NotImplementedError` in `to_dict()`:

```python
def to_dict(self, entry: dict) -> FeedEntry:
    return FeedEntry(
        url=entry["url"],
        title=entry["title"],
        date=entry.get("date", ""),
        source=self.name,
        summary="",
    )
```

- [ ] **Step 4: Run full test suite**

```
pytest tests/test_tiktok.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 5: Run full project test suite to catch regressions**

```
pytest -v
```

Expected: all tests `PASSED`

- [ ] **Step 6: Commit**

```
git add feedy/sources/tiktok.py tests/test_tiktok.py
git commit -m "feat(tiktok): implement to_dict(), complete TikTokSource"
```

---

### Task 5: Mark Day 07 complete in roadmap

**Files:**
- Modify: `roadmap.md`

- [ ] **Step 1: Update roadmap**

In `roadmap.md`, change:

```
- [ ] Day 07 — TikTokSource: scrape developers.tiktok.com/blog
```

to:

```
- [x] Day 07 — TikTokSource: scrape developers.tiktok.com/blog
```

- [ ] **Step 2: Commit**

```
git add roadmap.md
git commit -m "chore: mark Day 07 complete"
```
