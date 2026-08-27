from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://foundersfund.com"
_URL = f"{_BASE_URL}/anatomy-of-next/articles-essays-more/"
_RSS_URL = f"{_BASE_URL}/anatomy-of-next/feed/"


class FoundersFundSource(BaseFeedSource):
    """Scrapes Founders Fund Anatomy of Next content. Requires no credentials."""

    @property
    def name(self) -> str:
        return "foundersfund"

    def fetch(self) -> list:
        """Fetch HTML, trying RSS first."""
        try:
            response = httpx.get(_RSS_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            if "xml" in response.headers.get("content-type", "") or response.text.strip().startswith("<?xml"):
                return [response.text]
        except httpx.HTTPError:
            pass

        try:
            response = httpx.get(_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[FoundersFundSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Parse RSS or HTML into intermediate dicts."""
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

    articles = soup.select("article, .post, .entry, .article, .content-card, .post-card")
    if not articles:
        articles = soup.select("a[href*='/anatomy-of-next/']")

    for article in articles:
        title_el = article.select_one("h1, h2, h3, h4, .title, .post-title, .entry-title, .article-title")
        link_el = article.select_one("a[href]")
        date_el = article.select_one("time, .date, .post-date, .published, [class*='date']")
        author_el = article.select_one(".author, .post-author, [class*='author']")
        type_el = article.select_one(".type, .format, .post-type, [class*='type']")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        type_prefix = ""
        if type_el:
            post_type = type_el.get_text(strip=True)
            if post_type:
                type_prefix = f"[{post_type}] "
        if author_el:
            author = author_el.get_text(strip=True)
            if author and author not in title:
                title = f"{author}: {type_prefix}{title}"
        elif type_prefix:
            title = f"{type_prefix}{title}"

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
        "%d %B %Y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""