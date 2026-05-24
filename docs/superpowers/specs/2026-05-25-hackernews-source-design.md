# HackerNewsSource Design

**Date:** 2026-05-25
**Feature:** Day 06 — scrape `news.ycombinator.com`, parse titles + links + dates

> Replaced original X/developer.x.com source (404'd). HN chosen as substitute.

---

## Architecture

- **File:** `feedy/sources/hackernews.py`
- **Class:** `HackerNewsSource(BaseFeedSource)`
- Mirrors TelegramSource structure: fetch → parse → to_dict pipeline via `BaseFeedSource.run()`

## Interface

| Method | Signature | Returns |
|--------|-----------|---------|
| `name` | property | `"hackernews"` |
| `fetch()` | `() -> list` | `[html_string]` or `[]` on error |
| `parse(raw)` | `(list) -> list[dict]` | list of `{title, url, date}` dicts |
| `to_dict(entry)` | `(dict) -> FeedEntry` | normalized `FeedEntry` |

## HTML Selectors

| Element | Selector |
|---------|----------|
| Story row | `tr.athing` |
| Title + URL | `span.titleline > a` |
| Date | next sibling `<tr>` → `span.age[title]` |

## fetch()

- GET `https://news.ycombinator.com`, timeout=10, follow_redirects=True
- Success: return `[response.text]`
- Any `httpx.HTTPError`: print warning `[HackerNewsSource] fetch failed: {err}`, return `[]`

## parse()

- If `raw` is empty, return `[]`
- Soup `raw[0]` with `html.parser`
- Per `tr.athing`:
  - `span.titleline > a` → title text + href
  - If href doesn't start with `http`, prefix `https://news.ycombinator.com/`
  - Next sibling `<tr>` → `span.age[title]` → `_parse_date()`
  - Skip if no title element found

## to_dict()

```python
FeedEntry(url=entry["url"], title=entry["title"], date=entry.get("date", ""), source="hackernews", summary="")
```

## _parse_date()

- Input: `"2026-05-24T16:31:29 1779640289"` (title attr of `span.age`)
- Split on space, take first token, `datetime.fromisoformat()` → `"%Y-%m-%d"`
- Any parse failure → `""`

## Error Handling

| Case | Behavior |
|------|----------|
| HTTP error / timeout | warn + return `[]` |
| `raw` is `[]` | `parse()` returns `[]` |
| Story missing title | skipped |
| Story missing URL | filtered by `_is_valid()` |
| Date parse fails | `date=""`, entry still included |
| Relative URL (`item?id=...`) | prefixed with base URL |

## Out of Scope

- Pagination — first page only
- Authentication
- Custom exceptions — plain print warning until CLI (Day 09)
- Caching / rate limiting

## Testing

`tests/test_hackernews.py` — 15 tests covering:
- `parse()`: single story, relative URL expansion, absolute URL preservation, ISO date, multiple stories, missing title skip, empty input
- `to_dict()`: source name, empty summary, field preservation
- `_parse_date()`: ISO datetime with unix suffix, without suffix, unknown format, empty string
- `run()` filter via monkeypatch
