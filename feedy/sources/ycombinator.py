from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_FEED_URL = "https://www.ycombinator.com/blog/feed"
_BASE_URL = "https://www.ycombinator.com"


class YCombinatorSource(BaseFeedSource):
    """Fetches Y Combinator blog posts via RSS feed."""

    @property
    def name(self) -> str:
        return "ycombinator"

    def fetch(self) -> list:
        """Fetch the RSS feed, returning an empty list on any transport error."""
        try:
            response = httpx.get(_FEED_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[YCombinatorSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Parse RSS XML into intermediate dicts with title, url, date, tags."""
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "xml")
        items = soup.select("item")
        results = []
        seen = set()
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            pub_date_el = item.find("pubDate")
            if not title_el or not link_el:
                continue
            title = title_el.get_text(strip=True)
            url = link_el.get_text(strip=True)
            if url in seen:
                continue
            seen.add(url)
            date = ""
            if pub_date_el:
                date = _parse_date(pub_date_el.get_text(strip=True))
            results.append({
                "title": title,
                "url": url,
                "date": date,
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


def _parse_date(raw: str) -> str:
    """Coerce RSS pubDate (RFC 822/2822) to ISO date, or empty string on failure."""
    if not raw:
        return ""
    try:
        dt = parsedate_to_datetime(raw)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""