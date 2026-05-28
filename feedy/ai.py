from __future__ import annotations

import os

import anthropic

from feedy.config import load_config

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 300


def complete(prompt: str) -> str | None:
    """Call the Anthropic API with prompt; return text or None on any failure."""
    key = os.environ.get("ANTHROPIC_API_KEY") or (load_config().api_key or "")
    if not key:
        return None
    client = anthropic.Anthropic(api_key=key)
    try:
        message = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError:
        return None
    if not message.content or not hasattr(message.content[0], "text"):
        return None
    return message.content[0].text.strip()
