from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://developers.tiktok.com"
_BLOG_URL = f"{_BASE_URL}/blogs"
_CARD_SELECTOR = 'a[data-e2e="CardContainer"]'
_TITLE_SELECTOR = 'span[data-e2e="TUXText"]'


class TikTokSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "tiktok"

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
            print(f"[TikTokSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        raise NotImplementedError

    def to_dict(self, entry: dict) -> FeedEntry:
        raise NotImplementedError
