# XSource Design

**Date:** 2026-05-30
**Status:** Approved

## Overview

Add `XSource` to scrape blog post titles, URLs, and dates from the Twitter/X
developer blog (`developer.x.com/en/blog`). Backfills Day 06. Follows the same
pattern as `OpenAISource` and `MetaSource`.

## Architecture

No new dependencies. Uses `httpx` + `BeautifulSoup` (already in the project).

## Components

### `feedy/sources/x.py`

- `_BASE_URL = "https://developer.x.com"`
- `_BLOG_URL = "https://developer.x.com/en/blog"`
- Card selector: `a[href*="/en/blog/"]` — X dev blog posts live at `/en/blog/<slug>`
- Title: `card.select_one("h3").get_text(strip=True)` — skip card if missing
- Date: `card.select_one("time")` — prefer ISO `datetime` attribute, else parse visible text `"Apr 14, 2026"`
- `_parse_date(el)`: returns ISO 8601, `""` on failure or missing element
- `name` property returns `"x"`
- `fetch()`: `httpx.get` with 10s timeout, User-Agent header, returns `[response.text]`
- `parse(raw)`: skips cards missing `h3`; preserves absolute URLs, expands relative `/`-prefixed URLs; the bare `/en/blog` index link has no `h3`, so it is skipped
- `to_dict(entry)`: maps to `FeedEntry` with `source="x"`, `summary=""`

### `feedy/cli.py`

- Register `"x": XSource` in `_build_sources` registry.

### `feedy/config.py`

- Add `"x"` to `DEFAULT_SOURCES`.

### `tests/test_x.py`

Mirrors `test_openai.py`: two full cards, absolute URL, visible-text date,
missing `h3` (skipped), missing `time` (date `""`), plus `to_dict` and `run` tests.

## Error Handling

- `fetch()` catches `httpx.HTTPError`, prints message, returns `[]`
- `parse()` skips cards with no `h3`
- `_parse_date()` returns `""` on any `ValueError` or missing element

## Out of Scope

- Pagination, JS-rendered content, full-text article content
- Scraping individual tweets (developer blog only)
