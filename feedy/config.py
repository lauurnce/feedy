from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".feedy" / "config.toml"

DEFAULT_SOURCES = ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic"]
DEFAULT_OUTPUT_FORMAT = "markdown"


@dataclass
class Config:
    sources: list[str] = field(default_factory=lambda: list(DEFAULT_SOURCES))
    output_format: str = DEFAULT_OUTPUT_FORMAT
    api_key: str | None = None


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
    )
