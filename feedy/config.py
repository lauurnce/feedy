from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".feedy" / "config.toml"

DEFAULT_SOURCES = ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic", "x"]
DEFAULT_OUTPUT_FORMAT = "markdown"


@dataclass
class EmailConfig:
    """SMTP settings for email digest delivery; port defaults to 587."""
    host: str
    port: int = 587
    username: str | None = None
    password: str | None = None
    sender: str | None = None
    recipient: str | None = None


@dataclass
class Config:
    """Resolved run configuration, defaulting to DEFAULT_SOURCES and markdown output."""
    sources: list[str] = field(default_factory=lambda: list(DEFAULT_SOURCES))
    output_format: str = DEFAULT_OUTPUT_FORMAT
    api_key: str | None = None
    slack_webhook_url: str | None = None
    email: EmailConfig | None = None


def load_config(path: Path | None = None) -> Config:
    """Load config from a TOML file. Return defaults if the file is missing."""
    if path is None:
        path = CONFIG_PATH
    if not path.exists():
        return Config()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return Config(
        sources=data.get("sources", list(DEFAULT_SOURCES)),
        output_format=data.get("output_format", DEFAULT_OUTPUT_FORMAT),
        api_key=data.get("anthropic", {}).get("api_key"),
        slack_webhook_url=data.get("slack", {}).get("webhook_url"),
        email=_load_email(data.get("email")),
    )


def _load_email(table: dict | None) -> EmailConfig | None:
    """Build an EmailConfig from the [email] table, or None when the table is absent."""
    if not table:
        return None
    return EmailConfig(
        host=table.get("host", ""),
        port=table.get("port", 587),
        username=table.get("username"),
        password=table.get("password"),
        sender=table.get("sender"),
        recipient=table.get("recipient"),
    )
