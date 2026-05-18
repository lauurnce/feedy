from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://core.telegram.org"
_BLOG_URL = f"{_BASE_URL}/blog"


class TelegramSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "telegram"

    def fetch(self) -> list:
        try:
            response = httpx.get(_BLOG_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[TelegramSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        posts = soup.select("a.dev_blog_card_link_wrap")
        results = []
        for post in posts:
            href = post.get("href", "")
            if href.startswith("/"):
                href = f"{_BASE_URL}{href}"
            title_el = post.select_one("h4.dev_blog_card_title")
            date_el = post.select_one("div.dev_blog_card_date")
            if not title_el:
                continue
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
    for fmt in ("%B %d, %Y", "%d %B %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""
