from __future__ import annotations

from datetime import datetime
import defusedxml.ElementTree as ET

import httpx

from feedy.sources.base import BaseFeedSource, FeedEntry

_FEED_URL = "https://www.a16z.news/feed"


class A16ZSubstackSource(BaseFeedSource):
    """Fetches the a16z Substack RSS feed. Requires no credentials."""

    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "a16z-substack"

    def fetch(self) -> list:
        """Fetch the RSS feed XML, returning an empty list on any transport error."""
        try:
            response = httpx.get(
                _FEED_URL,
                timeout=10,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[A16ZSubstackSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Parse RSS XML into intermediate dicts, deduplicating by URL."""
        if not raw:
            return []

        root = ET.fromstring(raw[0])
        results = []
        seen_urls: set[str] = set()

        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_date_el = item.find("pubDate")
            description_el = item.find("description")

            if title_el is None or link_el is None:
                continue

            title = title_el.text or ""
            url = link_el.text or ""

            if not title or not url:
                continue

            if url in seen_urls:
                continue
            seen_urls.add(url)

            date_str = ""
            if pub_date_el is not None and pub_date_el.text:
                date_str = _parse_date(pub_date_el.text)

            results.append({
                "title": title,
                "url": url,
                "date": date_str,
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
    """Coerce RFC 822 / RFC 2822 date to ISO date (YYYY-MM-DD), or empty string on failure."""
    if not raw:
        return ""

    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S",
        "%d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %Z",
        "%d %b %Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return ""