# OpenAISource Design

**Date:** 2026-05-30
**Status:** Approved

## Overview

Add `OpenAISource` to scrape blog post titles, URLs, and dates from `openai.com/news`. Kicks off Week 5 (community sources). Follows the same pattern as `MetaSource` and `TikTokSource`.

## Architecture

No new dependencies. Uses `httpx` + `BeautifulSoup` (already in the project).

## Components

### `feedy/sources/openai.py`

- `_BASE_URL = "https://openai.com"`
- `_BLOG_URL = "https://openai.com/news/"`
- Card selector: `a[href*="/index/"]` — OpenAI posts live at `/index/<slug>/`
- Title: `card.select_one("h3").get_text(strip=True)` — skip card if missing
- Date: `card.select_one("time")` — prefer ISO `datetime` attribute, else parse visible text `"Apr 14, 2026"`
- `_parse_date(el)`: returns ISO 8601, `""` on failure or missing element
- `name` property returns `"openai"`
- `fetch()`: `httpx.get` with 10s timeout, User-Agent header, returns `[response.text]`
- `parse(raw)`: skips cards missing `h3`; preserves absolute URLs, expands relative `/`-prefixed URLs
- `to_dict(entry)`: maps to `FeedEntry` with `source="openai"`, `summary=""`

### `feedy/cli.py`

- Register `"openai": OpenAISource` in `_build_sources` registry.

### `feedy/config.py`

- Add `"openai"` to `DEFAULT_SOURCES`.

### `tests/test_openai.py`

Fixture HTML covers:
- Two full cards (title + `time[datetime]` + relative URL)
- One card with absolute URL
- One card with visible-text date only (no `datetime` attr)
- One card missing `h3` (should be skipped)
- One card missing `time` (date falls back to `""`)

Tests mirror `test_meta.py`:
- `test_source_name` — `source.name == "openai"`
- `test_parse_returns_entries_from_valid_html` — count == 2
- `test_parse_extracts_title`
- `test_parse_expands_relative_url`
- `test_parse_preserves_absolute_url`
- `test_parse_parses_datetime_attr_to_iso`
- `test_parse_parses_visible_text_date_to_iso`
- `test_parse_empty_date_on_missing_time`
- `test_parse_skips_card_with_no_title`
- `test_parse_returns_empty_for_empty_input`
- `test_to_dict_sets_source_to_openai`
- `test_to_dict_sets_empty_summary`
- `test_to_dict_preserves_url_and_title`
- `test_run_filters_out_entry_missing_title`

## Data Flow

```
fetch() → [html_string]
parse([html]) → [{"title": ..., "url": ..., "date": "2026-04-14"}, ...]
to_dict(entry) → FeedEntry
```

## Error Handling

- `fetch()` catches `httpx.HTTPError`, prints message, returns `[]`
- `parse()` skips cards with no `h3`
- `_parse_date()` returns `""` on any `ValueError` or missing element

## Out of Scope

- Pagination (only first page)
- JS-rendered content (static HTML sufficient)
- Full-text article content
