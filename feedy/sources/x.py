from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://docs.x.com"
_BLOG_URL = f"{_BASE_URL}/changelog"
_CONTENT_SELECTOR = '[data-component-part="update-content"]'
_LABEL_SELECTOR = '[data-component-part="update-label"]'


class XSource(BaseFeedSource):
    """X (Twitter) developer changelog at docs.x.com/changelog.

    The legacy developer.x.com blog is gone; the changelog is the live
    equivalent. It is a single page of dated entries (no per-post pages), so
    each entry URL is a deep-link anchor into the changelog.
    """

    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "x"

    def fetch(self) -> list:
        """Fetch the developer docs changelog HTML, returning an empty list on transport error."""
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
            print(f"[XSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Extract title, url and date from each changelog entry in the markup."""
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        results = []
        for content in soup.select(_CONTENT_SELECTOR):
            title_el = content.select_one("h3")
            if not title_el:
                continue
            title = title_el.get_text(strip=True).replace("​", "").strip()
            if not title:
                continue
            slug = title_el.get("id", "")
            url = f"{_BLOG_URL}#{slug}" if slug else _BLOG_URL
            results.append({
                "title": title,
                "url": url,
                "date": _parse_date(_find_label(content)),
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


def _find_label(content) -> str:
    """Walk up from an update-content block to the row holding its date label."""
    node = content
    for _ in range(4):
        node = node.parent
        if node is None:
            return ""
        label = node.select_one(_LABEL_SELECTOR)
        if label:
            return label.get_text(strip=True)
    return ""


def _parse_date(raw: str) -> str:
    if not raw:
        return ""
    try:
        return datetime.strptime(raw, "%b %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""
