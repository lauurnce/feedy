# feedy

Developer blog and VC news aggregator with AI-powered summaries.

`feedy` scrapes developer blogs and venture capital firm blogs from sources you
care about, stores new posts in a local SQLite database (deduplicated by URL),
and turns them into a concise daily digest — each item summarized in two
sentences plus a "why it matters for devs" line, courtesy of the Anthropic API.

## Sources

### Developer platforms (enabled by default)

| Source       | Name in config | Site |
| ------------ | -------------- | ---- |
| X (Twitter)  | `x`            | docs.x.com/changelog |
| Telegram     | `telegram`     | core.telegram.org/blog |
| TikTok       | `tiktok`       | developers.tiktok.com/blog |
| Meta         | `meta`         | developers.facebook.com/blog |
| OpenAI       | `openai`       | openai.com/news |
| Anthropic    | `anthropic`    | anthropic.com/news |
| Hacker News  | `hackernews`   | news.ycombinator.com |

### VC firms (opt-in — add to `sources` in your config)

Add any of these names to the `sources` list in `~/.feedy/config.toml` to
include them in `fetch` and `digest`. See [Configuration](#configuration).

| Firm | Name in config | Site |
| ---- | --------------- | ---- |
| Sequoia Capital | `sequoia` | sequoiacap.com |
| Sequoia Capital (Inference) | `sequoia-inference` | inferencebysequoia.substack.com |
| Andreessen Horowitz | `a16z` | a16z.com |
| Andreessen Horowitz (Substack) | `a16z-substack` | a16z.news |
| Y Combinator | `ycombinator` | ycombinator.com/blog |
| First Round Capital | `firstround` | review.firstround.com |
| First Round Capital (News) | `firstround-news` | firstround.com/news |
| Greylock | `greylock` | greylock.com |
| Lightspeed | `lightspeed` | lsvp.com |
| Index Ventures | `index` | indexventures.com |
| Union Square Ventures | `usv` | usv.com |
| Founders Fund | `foundersfund` | foundersfund.com |
| Khosla Ventures | `khosla` | khoslaventures.com |
| NEA | `nea` | nea.com |

Run `feedy sources` to list every registered source name from the CLI.

All developer-platform sources are enabled by default; VC sources are opt-in
so digests stay focused unless you ask for them. Adding a new source takes
about ten lines — see [CONTRIBUTING.md](CONTRIBUTING.md).

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
feedy list --source sequoia               # works for VC sources too
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

### Deliver the digest

```bash
feedy digest --slack                       # post to a Slack incoming webhook
feedy digest --email                       # send over SMTP to the recipient
```

`--slack` needs a webhook URL (`[slack] webhook_url` or `FEEDY_SLACK_WEBHOOK`).
`--email` needs the `[email]` SMTP settings (password via `[email] password` or
`FEEDY_SMTP_PASSWORD`). See [Configuration](#configuration).

### Serve the digest as JSON

```bash
feedy serve                                # http://127.0.0.1:8000
feedy serve --host 0.0.0.0 --port 9000
```

Exposes `GET /` (health) and `GET /digest?since=YYYY-MM-DD&source=NAME`, which
returns today's saved entries as JSON.

## Configuration

`feedy` reads an optional TOML config from `~/.feedy/config.toml`. If the file
is missing, sensible defaults are used (developer-platform sources enabled,
VC sources opt-in, Markdown output).

```toml
# ~/.feedy/config.toml

# Which sources to fetch and include in the digest.
# Defaults to the developer-platform sources; add VC firm names (e.g. "sequoia",
# "a16z", "ycombinator") to also pull VC news. Run `feedy sources` for the
# full list of registered names.
sources = ["x", "telegram", "tiktok", "meta", "openai", "anthropic", "hackernews"]

# Digest format: "markdown" (default) or "plain".
output_format = "markdown"

[anthropic]
# API key for AI summaries. The ANTHROPIC_API_KEY env var takes precedence.
api_key = "sk-ant-..."

[slack]
# Incoming webhook URL for `feedy digest --slack`.
# FEEDY_SLACK_WEBHOOK env var takes precedence.
webhook_url = "https://hooks.slack.com/services/..."

[email]
# SMTP settings for `feedy digest --email`.
# FEEDY_SMTP_PASSWORD env var takes precedence over `password`.
host = "smtp.gmail.com"
port = 587
username = "you@example.com"
password = "app-password"
sender = "you@example.com"
recipient = "you@example.com"
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
