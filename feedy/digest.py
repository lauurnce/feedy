from __future__ import annotations

from collections import defaultdict

from feedy.sources.base import FeedEntry


def build_digest(entries: list[FeedEntry]) -> str:
    """Group entries by source and format as a readable digest string."""
    if not entries:
        return ""

    groups: dict[str, list[FeedEntry]] = defaultdict(list)
    for entry in entries:
        groups[entry["source"]].append(entry)

    sections = []
    for source in sorted(groups):
        lines = [f"## {source.title()}"]
        for entry in groups[source]:
            if entry["summary"]:
                lines.append(f"• {entry['title']} — {entry['summary']}")
            else:
                lines.append(f"• {entry['title']}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
