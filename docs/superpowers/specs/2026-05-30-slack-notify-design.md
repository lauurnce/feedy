# Slack Webhook Output Design

**Date:** 2026-05-30
**Status:** Approved

## Overview

Add a Slack incoming-webhook output channel. `feedy digest --slack` POSTs the
rendered digest to a configured Slack webhook URL. Day 23.

## Architecture

No new dependencies. Uses `httpx` (already in the project).

## Components

### `feedy/notify.py`

- `send_to_slack(text: str, webhook_url: str) -> bool`
  - POSTs `{"text": text}` to `webhook_url` via `httpx.post`, 10s timeout.
  - `raise_for_status()`; returns `True` on success.
  - Catches `httpx.HTTPError`, prints `[slack] send failed: ...`, returns `False`.

### `feedy/config.py`

- `Config` gains `slack_webhook_url: str | None = None`.
- `load_config` reads `data.get("slack", {}).get("webhook_url")` (mirrors the
  existing `[anthropic] api_key` pattern).

### `feedy/cli.py`

- `digest` gains `--slack` flag.
- Webhook URL resolved as `os.environ.get("FEEDY_SLACK_WEBHOOK") or config.slack_webhook_url`
  (env wins, mirrors the `ANTHROPIC_API_KEY` precedence in `ai.py`).
- When `--slack` set:
  - No URL → `click.echo("No Slack webhook configured.", err=True)`.
  - `send_to_slack` True → `click.echo("Digest sent to Slack.")`.
  - False → `click.echo("Failed to send digest to Slack.", err=True)`.
- `--slack` is independent of stdout/`--output`; existing print/file behavior unchanged.

## Config example

```toml
[slack]
webhook_url = "https://hooks.slack.com/services/T00/B00/xxxx"
```

## Security

- Webhook URL is a secret (anyone with it can post). Read from config/env only;
  never committed. Documented in spec, not hardcoded.

## Tests

### `tests/test_notify.py`
- `send_to_slack` posts `json={"text": text}` to the URL.
- Returns `True` on 200.
- Returns `False` on `httpx.HTTPError`.

### `tests/test_cli.py`
- `--slack` with configured URL calls `send_to_slack(text, url)`.
- `--slack` env var overrides config URL.
- `--slack` with no URL prints "No Slack webhook configured."
- digest without `--slack` does not call `send_to_slack`.

### `tests/test_config.py`
- default `slack_webhook_url` is `None`.
- `[slack] webhook_url` loaded from file.

## Out of Scope

- Slack Block Kit formatting (plain `text` payload only)
- Retry/backoff on failure
- Other channels (email is Day 24)
