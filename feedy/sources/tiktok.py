from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://developers.tiktok.com"
_BLOG_URL = f"{_BASE_URL}/blogs"
_CARD_SELECTOR = 'a[data-e2e="CardContainer"]'
_TITLE_SELECTOR = 'span[data-e2e="TUXText"]'


class TikTokSource(BaseFeedSource):
    """Scrapes the TikTok for Developers changelog. Requires no credentials."""
    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "tiktok"

    def fetch(self) -> list:
        """Fetch the changelog HTML, returning an empty list on any transport error."""
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
            print(f"[TikTokSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Extract title, url and date from each changelog entry in the markup."""
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
            title_el = card.select_one(_TITLE_SELECTOR)
            if not title_el:
                continue
            results.append({
                "title": title_el.get_text(strip=True),
                "url": href,
                "date": "",
            })
        return results

    def to_dict(self, entry: dict) -> FeedEntry:
        """Normalise an intermediate dict onto FeedEntry, leaving summary empty."""
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )
