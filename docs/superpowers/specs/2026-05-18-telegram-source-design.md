# TelegramSource Design

**Date:** 2026-05-18
**Feature:** Day 04 — scrape `core.telegram.org/blog`, parse titles + links + dates

---

## Architecture

- **File:** `feedy/sources/telegram.py`
- **Class:** `TelegramSource(BaseFeedSource)`
- Follows existing fetch → parse → to_dict pipeline from `BaseFeedSource.run()`

## Interface

| Method | Signature | Returns |
|--------|-----------|---------|
| `name` | property | `"telegram"` |
| `fetch()` | `() -> list` | `[html_string]` or `[]` on error |
| `parse(raw)` | `(list) -> list[dict]` | list of `{title, url, date}` dicts |
| `to_dict(entry)` | `(dict) -> FeedEntry` | normalized `FeedEntry` |

## fetch()

- GET `https://core.telegram.org/blog` via `httpx.get()`
- Success: return `[response.text]`
- Any `httpx.HTTPStatusError`, `httpx.RequestError`, or timeout: print warning `[TelegramSource] fetch failed: {err}`, return `[]`

## parse()

- If `raw` is empty, return `[]` immediately
- Soup `raw[0]` with `html.parser`
- Find all `<div class="blog-widget">` blocks
- Per block:
  - Title + relative href from `<a class="blog-title">`
  - Prefix relative URLs with `https://core.telegram.org`
  - Date text from `<div class="date">`, parsed with `strptime(s, "%d %B %Y")` → ISO `"%Y-%m-%d"`
  - Date parse failure → `date=""`
- Return list of `{"title": str, "url": str, "date": str}` dicts

## to_dict()

Maps intermediate dict to `FeedEntry`:

```python
FeedEntry(
    url=entry["url"],
    title=entry["title"],
    date=entry["date"],
    source="telegram",
    summary="",
)
```

## Error Handling

| Case | Behavior |
|------|----------|
| HTTP error / timeout | warn + return `[]` |
| `raw` is `[]` | `parse()` returns `[]` immediately |
| Post missing title or URL | filtered by `BaseFeedSource._is_valid()` |
| Date parse fails | `date=""`, entry still included |
| Relative URL | prefix `https://core.telegram.org` in `parse()` |
| Selector mismatch (site changed) | `parse()` returns `[]`, no crash |

## Out of Scope

- Pagination — first page only
- Custom exceptions — plain print warning is sufficient until CLI (Day 09)
- Caching / rate limiting — added later if needed

## Testing

Day 05 will add `pytest` tests for this class. Key cases:
- Mock HTTP response with sample HTML → verify parsed entries
- Empty/malformed HTML → verify empty list returned
- Malformed date string → verify `date=""` fallback
