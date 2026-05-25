# TikTokSource Design

**Date:** 2026-05-25
**Day:** 07
**Status:** Approved

## Goal

Add `TikTokSource` that scrapes the TikTok developer blog (`developers.tiktok.com/blogs`) and returns normalized `FeedEntry` objects, consistent with existing sources.

## Target URL

- Listing page: `https://developers.tiktok.com/blogs`
- Individual post URL pattern: `https://developers.tiktok.com/blog/<slug>`
- Page 1 only (12 posts per page, 76 total across 7 pages)

## HTML Structure

The page is server-rendered. Blog cards use stable `data-e2e` test attributes:

- Card container: `a[data-e2e="CardContainer"]` — the anchor element itself, `href="/blog/<slug>"`
- Title: first `span[data-e2e="TUXText"]` inside each card
- Date: not available anywhere (listing, individual posts, RSS, sitemap all lack dates)

CSS class names (e.g. `css-1bh4b8b`) are Emotion-generated hashes that change on rebuild — not used.

## Architecture

New file: `feedy/sources/tiktok.py`

```
_BASE_URL = "https://developers.tiktok.com"
_BLOG_URL  = f"{_BASE_URL}/blogs"
_CARD_SELECTOR  = 'a[data-e2e="CardContainer"]'
_TITLE_SELECTOR = 'span[data-e2e="TUXText"]'

TikTokSource(BaseFeedSource)
  name     → "tiktok"
  fetch()  → GET _BLOG_URL with httpx, returns [html_text]
  parse()  → BeautifulSoup select cards → [{title, url, date=""}]
  to_dict()→ FeedEntry(url, title, date="", source="tiktok", summary="")
```

URL normalization: `href` is relative (`/blog/slug`) → prepend `_BASE_URL`.

## Error Handling

- `httpx.HTTPError` caught in `fetch()` → print warning, return `[]`
- `_is_valid()` in `BaseFeedSource` filters entries missing `url` or `title`
- Cards with no `TUXText` span are skipped silently

## Date Field

`date=""` (empty string). No date is exposed in the HTML or any feed format. `_is_valid()` only requires `url` and `title`, so entries remain valid.

## Tests

New file: `tests/test_tiktok.py` — offline HTML fixtures, no network calls.

| Test | What it checks |
|------|---------------|
| `test_parse_returns_entries_from_valid_html` | 2-card fixture → 2 results |
| `test_parse_expands_relative_url` | `/blog/slug` → full URL |
| `test_parse_skips_card_with_no_title` | card missing TUXText span → skipped |
| `test_parse_returns_empty_for_empty_input` | `parse([])` → `[]` |
| `test_to_dict_sets_source_to_tiktok` | `source == "tiktok"` |
| `test_to_dict_sets_empty_date_and_summary` | `date == ""`, `summary == ""` |
| `test_to_dict_preserves_url_and_title` | fields pass through unchanged |
| `test_run_filters_out_entry_missing_url` | `_is_valid` integration |

## Out of Scope

- Pagination (pages 2–7)
- Date scraping from individual post pages
- Category/tag extraction
