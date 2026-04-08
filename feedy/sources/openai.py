from __future__ import annotations

from email.utils import parsedate_to_datetime

import httpx
from defusedxml.ElementTree import ParseError, fromstring
from defusedxml.common import DefusedXmlException

from feedy.sources.base import BaseFeedSource, FeedEntry

_FEED_URL = "https://openai.com/news/rss.xml"


class OpenAISource(BaseFeedSource):
    """OpenAI news from openai.com/news/rss.xml.

    The HTML page (openai.com/news) is bot-blocked (403), but the RSS feed is
    served openly, so we parse that instead.
    """

    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "openai"

    def fetch(self) -> list:
        """Fetch the OpenAI news RSS feed, returning an empty list on any transport error."""
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
            print(f"[OpenAISource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Extract title, link and publication date from each RSS item."""
        if not raw:
            return []
        try:
            root = fromstring(raw[0])
        except (ParseError, DefusedXmlException):
            return []
        results = []
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not title or not link:
                continue
            results.append({
                "title": title,
                "url": link,
                "date": _parse_date(item.findtext("pubDate")),
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


def _parse_date(raw: str | None) -> str:
    """Coerce the RSS publication date to an ISO date, or empty string on failure."""
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return ""
