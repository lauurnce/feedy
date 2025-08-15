"""Generates three-sentence summaries for entries that lack one."""

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
    """Build the three-sentence summarisation prompt for a single entry."""
    return (
        "Summarize this developer blog post.\n\n"
        f"Title: {entry['title']}\n"
        f"URL: {entry['url']}\n"
        f"Source: {entry['source']}\n\n"
        "Write exactly 3 sentences using this format:\n"
        "Sentence 1: What was announced or changed.\n"
        "Sentence 2: The key technical detail or how it works.\n"
        'Sentence 3: Start with "Why it matters:" followed by the impact for developers.\n\n'
        "Example:\n"
        "Telegram launches Stories API for bots with support for rich media up to 100MB. "
        "Developers can create, schedule, and react to story interactions via a REST endpoint with OAuth scoping. "
        "Why it matters: Bots can now run announcement campaigns and interactive polls previously limited to human accounts."
    )
