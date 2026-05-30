from __future__ import annotations

import httpx


def send_to_slack(text: str, webhook_url: str) -> bool:
    """POST the digest text to a Slack incoming webhook. Return True on success."""
    try:
        response = httpx.post(webhook_url, json={"text": text}, timeout=10)
        response.raise_for_status()
        return True
    except httpx.HTTPError as err:
        print(f"[slack] send failed: {err}")
        return False
