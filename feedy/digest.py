"""Renders stored entries into a markdown or plain text digest."""

from __future__ import annotations

from collections import defaultdict

from feedy.sources.base import FeedEntry


def build_digest(entries: list[FeedEntry], output_format: str = "markdown") -> str:
    """Group entries by source and format as a readable digest string."""
    if not entries:
        return ""

    groups: dict[str, list[FeedEntry]] = defaultdict(list)
    for entry in entries:
        groups[entry["source"]].append(entry)

    sections = []
    for source in sorted(groups):
        if output_format == "plain":
            header = source.upper()
            bullet = "- "
        else:
            header = f"## {source.title()}"
            bullet = "• "
        lines = [header]
        for entry in groups[source]:
            if entry["summary"]:
                lines.append(f"{bullet}{entry['title']} — {entry['summary']}")
            else:
                lines.append(f"{bullet}{entry['title']}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
