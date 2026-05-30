from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://www.anthropic.com"
_BLOG_URL = f"{_BASE_URL}/news"
_CARD_SELECTOR = 'a[href*="/news/"]'


class AnthropicSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "anthropic"

    def fetch(self) -> list:
        try:
            response = httpx.get(
                _BLOG_URL,
                timeout=10,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[AnthropicSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        cards = soup.select(_CARD_SELECTOR)
        results = []
        for card in cards:
            href = card.get("href", "")
            if href.startswith("/"):
                href = f"{_BASE_URL}{href}"
            if not href:
                continue
            title_el = card.select_one("h3")
            if not title_el:
                continue
            results.append({
                "title": title_el.get_text(strip=True),
                "url": href,
                "date": _parse_date(card.select_one("time")),
            })
        return results

    def to_dict(self, entry: dict) -> FeedEntry:
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )


def _parse_date(el) -> str:
    if el is None:
        return ""
    iso = el.get("datetime", "")
    if iso:
        try:
            return datetime.fromisoformat(iso[:10]).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    try:
        return datetime.strptime(el.get_text(strip=True), "%b %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""
