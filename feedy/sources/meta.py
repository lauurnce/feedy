from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://developers.facebook.com"
_BLOG_URL = f"{_BASE_URL}/blog/"
_CARD_SELECTOR = 'a[href*="/blog/post/"]'


class MetaSource(BaseFeedSource):
    @property
    def name(self) -> str:
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
        return []

    def to_dict(self, entry: dict) -> FeedEntry:
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )
