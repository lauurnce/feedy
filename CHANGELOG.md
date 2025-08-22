# Changelog

All notable changes to this project are recorded here.

## Unreleased

### Added

- SQLite storage with url-based deduplication.
- `BaseFeedSource` abstract contract with the `FeedEntry` schema.
- Hacker News source scraping the front page.
- Anthropic and OpenAI news sources.
- Meta, Telegram, TikTok and X changelog sources.
- `fetch` command pulling every configured source.
- `list` command with `--limit` to cap output rows.
- `sources` command listing registered source names.
- `stats` command reporting entry counts per source.
