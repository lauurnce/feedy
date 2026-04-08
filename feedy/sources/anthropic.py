from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://www.anthropic.com"
_BLOG_URL = f"{_BASE_URL}/news"
_CARD_SELECTOR = 'a[href^="/news/"]'


class AnthropicSource(BaseFeedSource):
    """Scrapes the Anthropic news index. Requires no credentials."""
    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "anthropic"

    def fetch(self) -> list:
        """Fetch the news index HTML, returning an empty list on any transport error."""
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
        """Extract title, url and date from each article entry in the index markup."""
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        results = []
        seen = set()
        for card in soup.select(_CARD_SELECTOR):
            href = card.get("href", "")
            if not href:
                continue
            # Featured cards use a heading; grid cards use a title span whose
            # hashed module class still contains "title".
            title_el = card.find(["h1", "h2", "h3", "h4"]) or card.select_one('[class*="title"]')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue
            url = f"{_BASE_URL}{href}"
            if url in seen:
                continue
            seen.add(url)
            results.append({
                "title": title,
                "url": url,
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
    try:
        return datetime.strptime(el.get_text(strip=True), "%b %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""
