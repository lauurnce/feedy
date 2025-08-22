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
- `digest` command with `--format` for markdown or plain output.
- Anthropic-backed summariser producing three-sentence summaries.
- Slack delivery via `digest --slack`.
- Email delivery via `digest --email` over SMTP.
- Read-only JSON API serving stored entries.
- TOML configuration at `~/.feedy/config.toml` with env var precedence.
