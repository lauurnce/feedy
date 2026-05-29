# feedy

Developer blog feed aggregator with AI-powered summaries.

`feedy` scrapes developer blogs from platforms you care about, stores new posts
in a local SQLite database (deduplicated by URL), and turns them into a concise
daily digest — each item summarized in two sentences plus a "why it matters for
devs" line, courtesy of the Anthropic API.

## Sources

| Source       | Name in config | Site |
| ------------ | -------------- | ---- |
| Telegram     | `telegram`     | core.telegram.org/blog |
| TikTok       | `tiktok`       | developers.tiktok.com/blog |
| Meta         | `meta`         | developers.facebook.com/blog |
| Hacker News  | `hackernews`   | news.ycombinator.com |

More sources (X, OpenAI, Anthropic) are on the [roadmap](ROADMAP.md). Adding one
takes about ten lines — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Install

Requires Python 3.11+.

```bash
git clone https://github.com/<your-account>/feedy.git
cd feedy
pip install -e ".[dev]"
```

This installs the `feedy` command.

## Usage

```bash
feedy fetch                      # pull latest entries from configured sources
feedy list                       # show saved entries as a table
feedy digest                     # print today's AI digest
```

### Filtering

```bash
feedy list --source hackernews            # only one source
feedy list --since 2026-05-01             # on or after a date (YYYY-MM-DD)
feedy digest --since 2026-05-01           # digest over a date range
feedy digest --source meta                # digest for one source
```

### Export the digest to a file

```bash
feedy digest --output report.md           # write Markdown to a file
feedy digest -o report.md                 # short flag
```

When `--output` is given, the digest is written to the file instead of being
printed to the terminal.

## Configuration

`feedy` reads an optional TOML config from `~/.feedy/config.toml`. If the file
is missing, sensible defaults are used (all sources enabled, Markdown output).

```toml
# ~/.feedy/config.toml

# Which sources to fetch and include in the digest.
sources = ["telegram", "tiktok", "meta", "hackernews"]

# Digest format: "markdown" (default) or "plain".
output_format = "markdown"

[anthropic]
# API key for AI summaries. The ANTHROPIC_API_KEY env var takes precedence.
api_key = "sk-ant-..."
```

### API key

AI summaries need an Anthropic API key. `feedy` looks for it in this order:

1. `ANTHROPIC_API_KEY` environment variable
2. `anthropic.api_key` in `~/.feedy/config.toml`

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
feedy digest
```

Without a key, `fetch` and `list` still work; `digest` falls back to showing
titles without summaries.

## Automating daily fetches

The repo ships a GitHub Actions workflow
([`.github/workflows/fetch.yml`](.github/workflows/fetch.yml)) that runs
`feedy fetch` once a day at 06:00 UTC and caches the database between runs so
deduplication keeps working. Trigger it manually from the Actions tab via
**Run workflow**.

## Storage

Entries live in a SQLite database at `~/.feedy/feedy.db`. Posts are deduplicated
by URL, so re-running `fetch` only saves what's new.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full feature plan.
