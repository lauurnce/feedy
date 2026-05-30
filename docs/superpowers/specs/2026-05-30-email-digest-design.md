# Email Digest Output Design

**Date:** 2026-05-30
**Status:** Approved

## Overview

Add an email output channel. `feedy digest --email` sends the rendered digest
to a configured recipient over SMTP. Day 24.

## Architecture

No new dependencies. Uses stdlib `smtplib` + `email.message.EmailMessage`.
SMTP (not SendGrid) keeps the project dependency-free and works with any
provider (Gmail app password, Fastmail, self-hosted, etc.).

## Components

### `feedy/config.py`

New `EmailConfig` dataclass:

- `host: str`
- `port: int = 587`
- `username: str | None = None`
- `password: str | None = None`
- `sender: str | None = None`
- `recipient: str | None = None`

`Config` gains `email: EmailConfig | None = None`. `load_config` builds it from
the `[email]` TOML table when present, else `None`.

### `feedy/notify.py`

- `send_email(text: str, subject: str, cfg) -> bool`
  - Builds an `EmailMessage` (`Subject`, `From=cfg.sender`, `To=cfg.recipient`,
    plain-text body).
  - `smtplib.SMTP(cfg.host, cfg.port, timeout=10)` → `starttls()` →
    `login(username, password)` only when both present → `send_message`.
  - Returns `True` on success.
  - Catches `(smtplib.SMTPException, OSError)`, prints `[email] send failed: ...`,
    returns `False`.

### `feedy/cli.py`

- `digest` gains `--email` flag.
- Password resolved as `os.environ.get("FEEDY_SMTP_PASSWORD") or cfg.password`
  (env wins, mirrors Slack/`ANTHROPIC_API_KEY`); injected via `dataclasses.replace`.
- Subject: `f"feedy digest — {since}"`.
- When `--email` set:
  - No `config.email` or no `recipient` → `click.echo("No email configured.", err=True)`.
  - `send_email` True → `click.echo("Digest emailed.")`.
  - False → `click.echo("Failed to send email.", err=True)`.
- `--email` suppresses stdout body (like `--slack`); `--output` still writes file.

## Config example

```toml
[email]
host = "smtp.gmail.com"
port = 587
username = "you@gmail.com"
password = "app-password"
sender = "you@gmail.com"
recipient = "you@gmail.com"
```

## Security

- SMTP password is a secret. Read from config/env only (`FEEDY_SMTP_PASSWORD`
  preferred), never committed. Connection uses STARTTLS.

## Tests

### `tests/test_notify.py`
- `send_email` calls `send_message` on the SMTP server.
- Logs in when username + password present.
- Returns `True` on success, `False` on `smtplib.SMTPException`.

### `tests/test_cli.py`
- `--email` with configured recipient calls `send_email` with subject + cfg.
- `--email` env password overrides config password.
- `--email` with no email config warns.
- digest without `--email` does not call `send_email`.

### `tests/test_config.py`
- default `email` is `None`.
- `[email]` table loaded into `EmailConfig`.

## Out of Scope

- HTML email bodies (plain text only)
- SendGrid / API-based providers
- Multiple recipients
