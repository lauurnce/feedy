from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://greylock.com"
_BLOG_URL = f"{_BASE_URL}/blog/"
_RSS_URL = f"{_BASE_URL}/blog/feed/"

_SECTION_URLS = [
    _BLOG_URL,
    f"{_BASE_URL}/blog/portfolio-news/",
    f"{_BASE_URL}/blog/greymatter/",
    f"{_BASE_URL}/blog/firm-news/",
    f"{_BASE_URL}/change-agents/",
]


class GreylockSource(BaseFeedSource):
    """Scrapes the Greylock blog and sub-sections. Requires no credentials."""

    @property
    def name(self) -> str:
        return "greylock"

    def fetch(self) -> list:
        """Fetch blog HTML from all sections, trying RSS first."""
        try:
            response = httpx.get(_RSS_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            if "xml" in response.headers.get("content-type", "") or response.text.strip().startswith("<?xml"):
                return [response.text]
        except httpx.HTTPError:
            pass

        results = []
        for url in _SECTION_URLS:
            try:
                response = httpx.get(url, timeout=10, follow_redirects=True)
                response.raise_for_status()
                results.append(response.text)
            except httpx.HTTPError as err:
                print(f"[GreylockSource] fetch failed for {url}: {err}")
        return results

    def parse(self, raw: list) -> list[dict]:
        """Parse RSS or HTML from blog sections into intermediate dicts."""
        if not raw:
            return []

        entries = []
        seen_urls = set()

        for content in raw:
            if content.strip().startswith("<?xml") or "<rss" in content[:100] or "<feed" in content[:100]:
                entries.extend(_parse_rss(content, seen_urls))
            else:
                entries.extend(_parse_html(content, seen_urls))

        return entries

    def to_dict(self, entry: dict) -> FeedEntry:
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )


def _parse_rss(xml_text: str, seen_urls: set) -> list[dict]:
    from xml.etree import ElementTree as ET

    entries = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()

            if not link or link in seen_urls:
                continue
            seen_urls.add(link)

            date = _parse_date(pub_date)
            entries.append({"title": title, "url": link, "date": date})
    except Exception:
        pass
    return entries


def _parse_html(html: str, seen_urls: set) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    entries = []

    articles = soup.select("article, .post, .blog-post, .entry, .post-item, .story-card")
    if not articles:
        articles = soup.select("a[href*='/blog/'], a[href*='/change-agents/']")

    for article in articles:
        title_el = article.select_one("h1, h2, h3, .title, .post-title, .entry-title")
        link_el = article.select_one("a[href]")
        date_el = article.select_one("time, .date, .post-date, .entry-date, .published")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        href = link_el.get("href", "").strip()
        if not href:
            continue
        if href.startswith("/"):
            href = f"{_BASE_URL}{href}"

        if href in seen_urls:
            continue
        seen_urls.add(href)

        date = ""
        if date_el:
            date = _parse_date(date_el.get("datetime", "") or date_el.get_text(strip=True))

        entries.append({"title": title, "url": href, "date": date})

    return entries


def _parse_date(raw: str) -> str:
    if not raw:
        return ""
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""