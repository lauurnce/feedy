from abc import ABC, abstractmethod
from typing import TypedDict


class FeedEntry(TypedDict):
    url: str
    title: str
    date: str        # ISO 8601, e.g. "2026-05-16"
    source: str      # platform name, e.g. "telegram"
    summary: str     # empty string if not yet summarised


class BaseFeedSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique slug for this source, e.g. 'telegram'."""

    @abstractmethod
    def fetch(self) -> list:
        """Fetch raw data from the source. Return value is source-specific."""

    @abstractmethod
    def parse(self, raw: list) -> list[dict]:
        """Parse raw fetch output into intermediate dicts."""

    @abstractmethod
    def to_dict(self, entry: dict) -> FeedEntry:
        """Normalise a single intermediate dict to FeedEntry schema."""

    def run(self) -> list[FeedEntry]:
        """Fetch → parse → normalise. Returns validated FeedEntry list."""
        raw = self.fetch()
        entries = self.parse(raw)
        results = []
        for e in entries:
            normalised = self.to_dict(e)
            if self._is_valid(normalised):
                results.append(normalised)
        return results

    @staticmethod
    def _is_valid(entry: FeedEntry) -> bool:
        return bool(entry.get("url") and entry.get("title"))
