from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://developers.facebook.com"
_BLOG_URL = f"{_BASE_URL}/blog/"
_CARD_SELECTOR = 'a[href*="/blog/post/"]'


class MetaSource(BaseFeedSource):
    """Scrapes the Meta for Developers blog index. Requires no credentials."""
    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "meta"

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
            print(f"[MetaSource] fetch failed: {err}")
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
            date_el = card.select_one("h6")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": href,
                "date": _parse_date(date_el.get_text(strip=True) if date_el else ""),
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


def _parse_date(raw: str) -> str:
    try:
        return datetime.strptime(raw.title(), "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""
