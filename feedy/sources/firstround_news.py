from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://www.firstround.com"
_LIST_URL = f"{_BASE_URL}/news"
_ARTICLE_SELECTOR = "article.article-list__item"
_LINK_SELECTOR = "a.link.article-tile[href^='/news/']"


class FirstRoundNewsSource(BaseFeedSource):
    """Scrapes First Round News articles. Requires no credentials."""

    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "firstround-news"

    def fetch(self) -> list:
        """Fetch the news index HTML, returning an empty list on any transport error."""
        try:
            response = httpx.get(_LIST_URL, timeout=15, follow_redirects=True)
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[FirstRoundNewsSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Extract title, url and date per article, fetching article pages for dates."""
        if not raw:
            return []

        soup = BeautifulSoup(raw[0], "html.parser")
        articles = soup.select(_ARTICLE_SELECTOR)
        results = []
        seen_urls = set()

        for article in articles:
            link_el = article.select_one(_LINK_SELECTOR)
            if not link_el:
                continue

            href = link_el.get("href", "")
            if not href:
                continue

            if not href.startswith("http"):
                href = f"{_BASE_URL}{href}"

            if href in seen_urls:
                continue
            seen_urls.add(href)

            title = self._extract_title(link_el)
            if not title:
                continue

            date = self._fetch_article_date(href)

            results.append({
                "title": title,
                "url": href,
                "date": date,
            })

        return results

    def _extract_title(self, link_el) -> str:
        """Extract title from article tile h2 heading."""
        h2 = link_el.select_one("h2.article-tile__heading")
        if h2:
            return h2.get_text(strip=True)
        # Fallback: try to get from link text, removing 'News' prefix
        text = link_el.get_text(strip=True)
        if text.startswith("News"):
            text = text[4:].strip()
        return text

    def _fetch_article_date(self, url: str) -> str:
        """Fetch a single article page and extract the published date."""
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            time_el = soup.find("time")
            if time_el and time_el.get("datetime"):
                return _parse_date(time_el["datetime"])

            meta = soup.find("meta", property="article:published_time")
            if meta and meta.get("content"):
                return _parse_date(meta["content"])

        except httpx.HTTPError:
            pass

        return ""

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
    """Coerce various date formats to ISO date (YYYY-MM-DD), or empty string on failure."""
    if not raw:
        return ""

    raw = raw.strip()
    if "T" in raw:
        raw = raw.split("T")[0]

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return ""