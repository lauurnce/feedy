from abc import ABC, abstractmethod


class BaseFeedSource(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]:
        """Fetch raw data from the source."""

    @abstractmethod
    def parse(self, raw: list) -> list[dict]:
        """Parse raw data into structured entries."""

    @abstractmethod
    def to_dict(self, entry: dict) -> dict:
        """Normalize a single entry to standard schema."""

    def run(self) -> list[dict]:
        raw = self.fetch()
        entries = self.parse(raw)
        return [self.to_dict(e) for e in entries]
