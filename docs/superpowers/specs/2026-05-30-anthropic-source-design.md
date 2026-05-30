# AnthropicSource Design

**Date:** 2026-05-30
**Status:** Approved

## Overview

Add `AnthropicSource` to scrape blog post titles, URLs, and dates from `anthropic.com/news`. Day 22. Follows the same pattern as `OpenAISource` and `MetaSource`.

## Architecture

No new dependencies. Uses `httpx` + `BeautifulSoup` (already in the project).

## Components

### `feedy/sources/anthropic.py`

- `_BASE_URL = "https://www.anthropic.com"`
- `_BLOG_URL = "https://www.anthropic.com/news"`
- Card selector: `a[href*="/news/"]` — Anthropic posts live at `/news/<slug>`
- Title: `card.select_one("h3").get_text(strip=True)` — skip card if missing
- Date: `card.select_one("time")` — prefer ISO `datetime` attribute, else parse visible text `"Apr 14, 2026"`
- `_parse_date(el)`: returns ISO 8601, `""` on failure or missing element
- `name` property returns `"anthropic"`
- `fetch()`: `httpx.get` with 10s timeout, User-Agent header, returns `[response.text]`
- `parse(raw)`: skips cards missing `h3`; preserves absolute URLs, expands relative `/`-prefixed URLs; the bare `/news` index link has no `h3`, so it is skipped
- `to_dict(entry)`: maps to `FeedEntry` with `source="anthropic"`, `summary=""`

### `feedy/cli.py`

- Register `"anthropic": AnthropicSource` in `_build_sources` registry.

### `feedy/config.py`

- Add `"anthropic"` to `DEFAULT_SOURCES`.

### `tests/test_anthropic.py`

Mirrors `test_openai.py`: two full cards, absolute URL, visible-text date, missing `h3` (skipped), missing `time` (date `""`), plus `to_dict` and `run` tests.

## Error Handling

- `fetch()` catches `httpx.HTTPError`, prints message, returns `[]`
- `parse()` skips cards with no `h3`
- `_parse_date()` returns `""` on any `ValueError` or missing element

## Out of Scope

- Pagination, JS-rendered content, full-text article content
