## Week 1 — Foundation
- [x] Day 01 — Scaffold project: pyproject.toml, folder structure, .gitignore, README stub
- [x] Day 02 — BaseFeedSource abstract class with fetch(), parse(), to_dict()
- [x] Day 03 — SQLite storage module with save and dedup by URL
- [ ] Day 04 — TelegramSource: scrape core.telegram.org/blog, parse titles + links + dates
- [ ] Day 05 — pytest setup + tests for TelegramSource and SQLite storage

## Week 2 — More Sources
- [ ] Day 06 — XSource: scrape Twitter/X developer blog (developer.twitter.com)
- [ ] Day 07 — TikTokSource: scrape developers.tiktok.com/blog
- [ ] Day 08 — MetaSource: scrape developers.facebook.com/blog
- [ ] Day 09 — CLI entry point: `feedwise fetch` command using Click
- [ ] Day 10 — CLI: `feedwise list` — show saved entries from DB in terminal

## Week 3 — AI Summarizer
- [ ] Day 11 — Anthropic API integration module (client wrapper + error handling)
- [ ] Day 12 — Summarizer: takes raw entries, returns 2-sentence AI summary per item
- [ ] Day 13 — Digest builder: groups entries by platform, formats into readable digest
- [ ] Day 14 — CLI: `feedwise digest` — run summarizer and print today's digest
- [ ] Day 15 — Prompt tuning: improve summary quality, add "why it matters for devs" line

## Week 4 — Polish
- [ ] Day 16 — Config file support: sources to track, API key, output format (YAML/TOML)
- [ ] Day 17 — Export digest to Markdown file (feedwise digest --output report.md)
- [ ] Day 18 — GitHub Actions workflow: run `feedwise fetch` daily on schedule
- [ ] Day 19 — Full README with install guide, usage examples, screenshot
- [ ] Day 20 — CONTRIBUTING.md + guide for adding a new source in 10 lines

## Week 5+ — Community Features
- [ ] Day 21 — OpenAI blog source
- [ ] Day 22 — Anthropic blog source
- [ ] Day 23 — Slack webhook notification output
- [ ] Day 24 — Email digest output (via SendGrid or SMTP)
- [ ] Day 25 — Web UI: simple FastAPI endpoint that serves today's digest as JSON
...