# MetaSource Design

**Date:** 2026-05-26
**Status:** Approved

## Overview

Add `MetaSource` to scrape blog post titles, URLs, and dates from `developers.facebook.com/blog`. Follows the same pattern as `TelegramSource` and `TikTokSource`.

## Architecture

No new dependencies. Uses `httpx` + `BeautifulSoup` (already in the project).

## Components

### `feedy/sources/meta.py`

- `_BASE_URL = "https://developers.facebook.com"`
- `_BLOG_URL = "https://developers.facebook.com/blog/"`
- Card selector: `a[href*="/blog/post/"]` — targets only blog post anchor elements
- Title: `card.select_one("h3").get_text(strip=True)`
- Date: `card.select_one("h6").get_text(strip=True)` in format `"APRIL 14, 2026"`
- `_parse_date(raw)`: converts raw string to ISO 8601 via `.title()` + `strptime("%B %d, %Y")`, returns `""` on failure
- `name` property returns `"meta"`
- `fetch()`: `httpx.get` with 10s timeout, User-Agent header, returns `[response.text]`
- `parse(raw)`: skips cards missing `h3`; preserves absolute URLs, expands relative `/`-prefixed URLs
- `to_dict(entry)`: maps to `FeedEntry` with `source="meta"`, `summary=""`

### `tests/test_meta.py`

Fixture HTML covers:
- Two full cards (title + date + relative URL)
- One card with absolute URL
- One card missing `h3` (should be skipped)
- One card missing `h6` (date falls back to `""`)

Tests:
- `test_source_name` — `source.name == "meta"`
- `test_parse_returns_entries_from_valid_html` — count == 2
- `test_parse_extracts_title` — correct titles
- `test_parse_expands_relative_url` — `/blog/post/x` → full URL
- `test_parse_preserves_absolute_url`
- `test_parse_parses_date_to_iso` — `"APRIL 14, 2026"` → `"2026-04-14"`
- `test_parse_empty_date_on_missing_h6`
- `test_parse_skips_card_with_no_title`
- `test_parse_returns_empty_for_empty_input`
- `test_to_dict_sets_source_to_meta`
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
- `_parse_date()` returns `""` on any `ValueError`

## Out of Scope

- Pagination (only first page)
- JS-rendered content (static HTML sufficient based on page inspection)
- Full-text article content
