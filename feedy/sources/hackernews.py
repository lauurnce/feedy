from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://news.ycombinator.com"
_FEED_URL = _BASE_URL

_STORY_SELECTOR = "tr.athing"
_TITLE_SELECTOR = "span.titleline > a"


class HackerNewsSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "hackernews"

    def fetch(self) -> list:
        try:
            response = httpx.get(_FEED_URL, timeout=10, follow_redirects=True)
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[HackerNewsSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")
        stories = soup.select(_STORY_SELECTOR)
        results = []
        for story in stories:
            title_el = story.select_one(_TITLE_SELECTOR)
            if not title_el:
                continue
            href = title_el.get("href", "")
            if not href.startswith("http"):
                href = f"{_BASE_URL}/{href}"
            subtext_row = story.find_next_sibling("tr")
            date = ""
            if subtext_row:
                age_el = subtext_row.find("span", class_="age")
                if age_el:
                    date = _parse_date(age_el.get("title", ""))
            results.append({
                "title": title_el.get_text(strip=True),
                "url": href,
                "date": date,
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
    if not raw:
        return ""
    ts = raw.split()[0]
    try:
        return datetime.fromisoformat(ts).strftime("%Y-%m-%d")
    except ValueError:
        return ""
