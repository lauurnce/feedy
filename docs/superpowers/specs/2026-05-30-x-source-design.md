# XSource Design

**Date:** 2026-05-30
**Status:** Approved (revised after live verification)

## Overview

Add `XSource` to scrape the X (Twitter) developer changelog at
`docs.x.com/changelog`. Backfills Day 06.

**Note:** the legacy `developer.x.com/en/blog` / `developer.twitter.com/en/blog`
dev blog is gone (redirects to a 404), and `blog.x.com` is bot-blocked (403,
JS-rendered). The `docs.x.com/changelog` page is the live, scrapable equivalent
and was verified to return 190 dated entries.

## Architecture

No new dependencies. Uses `httpx` + `BeautifulSoup`.

## Live DOM (Mintlify "update" component)

Each changelog entry is a row:

```html
<div> <!-- row -->
  <div><div data-component-part="update-label">May 4, 2026</div>
       <div data-component-part="update-description">X API v2</div></div>
  <div><div data-component-part="update-content">
       <h3 id="entry-slug">​Entry title</h3> ...</div></div>
</div>
```

## Components

### `feedy/sources/x.py`

- `_BASE_URL = "https://docs.x.com"`, `_BLOG_URL = "https://docs.x.com/changelog"`
- Iterate `[data-component-part="update-content"]` blocks.
- Title: `h3` text, stripped of the leading zero-width space (`​`); skip if missing/empty.
- URL: `f"{_BLOG_URL}#{h3['id']}"` — the changelog is one page, so entries are
  deep-link anchors (unique, dedup-safe).
- Date: `_find_label(content)` walks up ≤4 parents to the row's
  `[data-component-part="update-label"]`; `_parse_date` parses `"May 4, 2026"`
  via `strptime("%b %d, %Y")`, `""` on failure.
- `name` returns `"x"`.
- `fetch()`: `httpx.get` 10s timeout, User-Agent header, returns `[response.text]`.
- `to_dict`: `FeedEntry` with `source="x"`, `summary=""`.

### `feedy/cli.py` / `feedy/config.py`

- Registered as `"x": XSource`; `"x"` in `DEFAULT_SOURCES`.

### `tests/test_x.py`

Fixture HTML mirrors the live row/label/content structure: two entries, a
content block with no `h3` (skipped), an entry with no label (date `""`), plus
`to_dict` and `run` tests.

## Error Handling

- `fetch()` catches `httpx.HTTPError`, prints, returns `[]`.
- `parse()` skips blocks with no/empty `h3`.
- `_parse_date()` returns `""` on `ValueError`.

## Out of Scope

- Pagination / lazy-loaded older entries (first page only)
- `blog.x.com` consumer blog (JS + bot protection)
- Full entry body text
