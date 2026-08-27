from __future__ import annotations

from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from feedy.sources.base import BaseFeedSource, FeedEntry

_BASE_URL = "https://sequoiacap.com"
_STORIES_URL = f"{_BASE_URL}/stories"


class SequoiaSource(BaseFeedSource):
    """Scrapes the Sequoia Capital stories index. Requires no credentials."""

    @property
    def name(self) -> str:
        """Registry slug for this source."""
        return "sequoia"

    def fetch(self) -> list:
        """Fetch the stories index HTML, returning an empty list on any transport error."""
        try:
            response = httpx.get(
                _STORIES_URL,
                timeout=10,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            return [response.text]
        except httpx.HTTPError as err:
            print(f"[SequoiaSource] fetch failed: {err}")
            return []

    def parse(self, raw: list) -> list[dict]:
        """Extract title, url and date from each story entry in the markup."""
        if not raw:
            return []
        soup = BeautifulSoup(raw[0], "html.parser")

        # Try multiple selectors for story cards
        story_cards = (
            soup.select("article.story-card")
            or soup.select(".story-card")
            or soup.select("article[class*='story']")
            or soup.select("[class*='story-card']")
        )

        results = []
        seen_urls = set()
        for card in story_cards:
            entry = self._parse_card(card)
            if entry and entry["url"] not in seen_urls:
                seen_urls.add(entry["url"])
                results.append(entry)
        return results

    def _parse_card(self, card) -> dict | None:
        """Parse a single story card element."""
        # Try multiple title selectors
        title_el = (
            card.select_one("h2 a")
            or card.select_one("h3 a")
            or card.select_one(".story-title a")
            or card.select_one("a[href*='/stories/']")
            or card.select_one("a")
        )
        if not title_el:
            return None

        href = title_el.get("href", "")
        if not href:
            return None
        if href.startswith("/"):
            href = f"{_BASE_URL}{href}"

        title = title_el.get_text(strip=True)
        if not title:
            return None

        # Try multiple date selectors
        date_el = (
            card.select_one("time")
            or card.select_one(".date")
            or card.select_one("[class*='date']")
            or card.select_one("[datetime]")
        )
        date_str = ""
        if date_el:
            # Prefer datetime attribute if present
            date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)

        return {
            "title": title,
            "url": href,
            "date": _parse_date(date_str),
        }

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
    """Coerce the story timestamp to an ISO date, or empty string on failure."""
    if not raw:
        return ""
    # Handle ISO format from datetime attribute
    if "T" in raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError:
            pass
    # Common formats: "Aug 26, 2026", "August 26, 2026", "26 Aug 2026"
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""