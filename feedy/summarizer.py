from __future__ import annotations

from feedy.ai import complete
from feedy.sources.base import FeedEntry


def summarize(entries: list[FeedEntry]) -> list[FeedEntry]:
    """Return new list of entries with summary populated via AI. Skips already-summarized."""
    results = []
    for entry in entries:
        if entry["summary"]:
            results.append(dict(entry))
        else:
            summary = complete(_build_prompt(entry)) or ""
            results.append({**entry, "summary": summary})
    return results


def _build_prompt(entry: FeedEntry) -> str:
    return (
        "Summarize this developer blog post in exactly 2 sentences.\n"
        f"Title: {entry['title']}\n"
        f"URL: {entry['url']}\n"
        f"Source: {entry['source']}\n\n"
        "Focus on what changed or was announced and why it matters to developers."
    )
