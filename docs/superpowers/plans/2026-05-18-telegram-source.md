# TelegramSource Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `TelegramSource` that scrapes `core.telegram.org/blog` and returns a list of `FeedEntry` dicts.

**Architecture:** Single class `TelegramSource` in `feedy/sources/telegram.py` extending `BaseFeedSource`. `fetch()` returns `[html_string]` or `[]` on HTTP error. `parse()` soups the HTML and extracts post dicts. `to_dict()` maps to `FeedEntry`. First page only — no pagination.

**Tech Stack:** Python 3.11+, httpx, beautifulsoup4 (html.parser)

---

### Task 1: Verify HTML selectors

**Files:**
- No files changed — read-only inspection

- [ ] **Step 1: Fetch and inspect the blog HTML**

Run in a Python REPL (not a file):

```python
import httpx
from bs4 import BeautifulSoup

r = httpx.get("https://core.telegram.org/blog", timeout=10, follow_redirects=True)
soup = BeautifulSoup(r.text, "html.parser")

posts = soup.select("div.blog-widget")
print(f"Found {len(posts)} post containers")

if posts:
    print(posts[0].prettify()[:1500])
```

- [ ] **Step 2: Confirm or correct the three selectors**

From the printed HTML, verify:

| What | Expected selector | Expected value |
|------|------------------|----------------|
| Post container | `div.blog-widget` | wraps one post |
| Title + href | `a.blog-title` | text = title, href = relative path |
| Date | `div.date` | text like `"15 May 2026"` |

If any selector is wrong, note the correct one. You will substitute it in Task 2.

---

### Task 2: Implement TelegramSource

**Files:**
- Create: `feedy/sources/telegram.py`

- [ ] **Step 1: Create `feedy/sources/telegram.py`**

```python
from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://core.telegram.org"
_BLOG_URL = f"{_BASE_URL}/blog"


class TelegramSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "telegram"

    def fetch(self) -> list:
        try:
            response = httpx.get(_BLOG_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[TelegramSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        posts = soup.select("div.blog-widget")
        results = []
        for post in posts:
            anchor = post.select_one("a.blog-title")
            date_el = post.select_one("div.date")
            if not anchor:
                continue
            href = anchor.get("href", "")
            if href.startswith("/"):
                href = f"{_BASE_URL}{href}"
            results.append({
                "title": anchor.get_text(strip=True),
                "url": href,
                "date": _parse_date(date_el.get_text(strip=True) if date_el else ""),
            })
        return results

    def to_dict(self, entry: dict) -> FeedEntry:
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )


def _parse_date(raw: str) -> str:
    for fmt in ("%d %B %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""
```

- [ ] **Step 2: Adjust selectors if Task 1 found different ones**

If Task 1 revealed different selectors, update the three `soup.select` / `post.select_one` calls in `parse()` before continuing. No other changes needed.

- [ ] **Step 3: Commit**

```bash
git add feedy/sources/telegram.py
git commit -m "feat: add TelegramSource for core.telegram.org/blog"
```

---

### Task 3: Smoke test

**Files:**
- Modify: `roadmap.md` (mark Day 04 complete)

- [ ] **Step 1: Run TelegramSource manually**

Run in a Python REPL from the project root:

```python
from feedy.sources.telegram import TelegramSource

src = TelegramSource()
entries = src.run()
print(f"Got {len(entries)} entries")
for e in entries[:3]:
    print(e)
```

Expected output: 5 or more entries, each a dict with non-empty `url` (starting with `https://core.telegram.org`), non-empty `title`, `source="telegram"`, `summary=""`.

If `entries` is empty and no error was printed: selectors are wrong — go back to Task 1.

- [ ] **Step 2: Mark Day 04 complete in roadmap.md**

In `roadmap.md` change:

```
- [ ] Day 04 — TelegramSource: scrape core.telegram.org/blog, parse titles + links + dates
```

to:

```
- [x] Day 04 — TelegramSource: scrape core.telegram.org/blog, parse titles + links + dates
```

- [ ] **Step 3: Commit**

```bash
git add roadmap.md
git commit -m "chore: mark Day 04 complete"
```
