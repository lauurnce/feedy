from unittest.mock import patch

import pytest

from feedy.summarizer import summarize


_ENTRY = {
    "url": "https://example.com/post",
    "title": "Example Post",
    "date": "2026-05-29",
    "source": "telegram",
    "summary": "",
}


def test_summarize_calls_complete_for_unsummarized_entry():
    entry = {**_ENTRY, "summary": ""}
    with patch("feedy.summarizer.complete", return_value="Two sentence summary.") as mock_complete:
        result = summarize([entry])
    mock_complete.assert_called_once()
    assert result[0]["summary"] == "Two sentence summary."


def test_summarize_skips_already_summarized_entry():
    entry = {**_ENTRY, "summary": "Already summarized."}
    with patch("feedy.summarizer.complete") as mock_complete:
        result = summarize([entry])
    mock_complete.assert_not_called()
    assert result[0]["summary"] == "Already summarized."


def test_summarize_sets_empty_summary_when_complete_returns_none():
    entry = {**_ENTRY, "summary": ""}
    with patch("feedy.summarizer.complete", return_value=None):
        result = summarize([entry])
    assert result[0]["summary"] == ""


def test_summarize_empty_input_returns_empty_list():
    result = summarize([])
    assert result == []


def test_summarize_does_not_mutate_input():
    entry = {**_ENTRY, "summary": ""}
    with patch("feedy.summarizer.complete", return_value="New summary."):
        summarize([entry])
    assert entry["summary"] == ""


def test_summarize_prompt_contains_title_url_source():
    entry = {**_ENTRY}
    with patch("feedy.summarizer.complete", return_value="Summary.") as mock_complete:
        summarize([entry])
    prompt = mock_complete.call_args.args[0]
    assert entry["title"] in prompt
    assert entry["url"] in prompt
    assert entry["source"] in prompt
