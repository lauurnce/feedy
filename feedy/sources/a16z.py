from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://a16z.com"
_NEWS_CONTENT_URL = f"{_BASE_URL}/news-content/"


class A16ZSource(BaseFeedSource):
    """Scrapes the a16z news content page. Requires no credentials."""

    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "a16z"

    def fetch(self) -> list:
        """Fetch the news content page HTML, returning an empty list on any transport error."""
        try:
            response = httpx.get(
                _NEWS_CONTENT_URL,
                timeout=10,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[A16ZSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Extract title, url and date from each article card in the markup."""
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        results = []
        seen_urls: set[str] = set()

        article_selectors = [
            "article",
            ".post-card",
            ".article-card",
            ".news-card",
            "[class*='post']",
            "[class*='article']",
            ".card",
        ]

        articles = []
        for selector in article_selectors:
            found = soup.select(selector)
            if found:
                articles = found
                break

        for article in articles:
            title_el = article.select_one("h2, h3, .post-title, .article-title, .card-title, a")
            if not title_el:
                continue

            link_el = title_el if title_el.name == "a" else article.select_one("a")
            if not link_el:
                continue

            href = link_el.get("href", "")
            if not href:
                continue
            if href.startswith("/"):
                href = f"{_BASE_URL}{href}"
            elif not href.startswith("http"):
                href = f"{_BASE_URL}/{href}"

            if href in seen_urls:
                continue
            seen_urls.add(href)

            title = title_el.get_text(strip=True)
            if not title:
                continue

            date_el = article.select_one("time[datetime], .date, .post-date, .article-date, [class*='date']")
            date_str = ""
            if date_el:
                if date_el.name == "time" and date_el.get("datetime"):
                    date_str = _parse_date(date_el["datetime"])
                else:
                    date_str = _parse_date(date_el.get_text(strip=True))

            results.append({
                "title": title,
                "url": href,
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
    """Coerce various timestamp formats to an ISO date (YYYY-MM-DD), or empty string on failure."""
    if not raw:
        return ""

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return ""