from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://www.usv.com"
_WRITING_URL = f"{_BASE_URL}/writing/"
_RSS_URL = "https://paragraph.com/api/blogs/rss/@usv"


class USVSource(BaseFeedSource):
    """Scrapes USV writing and Paragraph RSS feed. Requires no credentials."""

    @property
    def name(self) -> str:
        return "usv"

    def fetch(self) -> list:
        """Fetch from Paragraph RSS first, then writing page as fallback."""
        results = []

        try:
            response = httpx.get(_RSS_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            if "xml" in response.headers.get("content-type", "") or response.text.strip().startswith("<?xml"):
                results.append(response.text)
        except httpx.HTTPError as err:
            print(f"[USVSource] RSS fetch failed: {err}")

        try:
            response = httpx.get(_WRITING_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            results.append(response.text)
        except httpx.HTTPError as err:
            print(f"[USVSource] writing page fetch failed: {err}")

        return results

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

    posts = soup.select(".post, .writing-post, article, .entry, .post-item, [class*='post']")
    if not posts:
        posts = soup.select("a[href*='/writing/']")

    for post in posts:
        title_el = post.select_one("h1, h2, h3, h4, .title, .post-title, .entry-title")
        link_el = post.select_one("a[href]")
        date_el = post.select_one("time, .date, .post-date, .published, [class*='date']")
        author_el = post.select_one(".author, .post-author, [class*='author']")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        if author_el:
            author = author_el.get_text(strip=True)
            if author and author not in title:
                title = f"{author}: {title}"

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