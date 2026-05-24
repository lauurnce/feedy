import textwrap

import pytest

from feedy.sources.hackernews import HackerNewsSource, _parse_date


_SINGLE_STORY_HTML = textwrap.dedent("""\
    <html><body><table>
    <tr class="athing submission" id="1">
        <td class="title"><span class="titleline"><a href="https://example.com/story">Test Story Title</a></span></td>
    </tr>
    <tr>
        <td class="subtext"><span class="subline">
            <span class="age" title="2026-05-24T16:31:29 123456"><a href="item?id=1">2 hours ago</a></span>
        </span></td>
    </tr>
    </table></body></html>
""")

_TWO_STORIES_HTML = textwrap.dedent("""\
    <html><body><table>
    <tr class="athing submission" id="1">
        <td class="title"><span class="titleline"><a href="https://first.com">First Story</a></span></td>
    </tr>
    <tr>
        <td class="subtext">
            <span class="age" title="2026-05-24T10:00:00 1"><a href="item?id=1">5 hours ago</a></span>
        </td>
    </tr>
    <tr class="athing submission" id="2">
        <td class="title"><span class="titleline"><a href="https://second.com">Second Story</a></span></td>
    </tr>
    <tr>
        <td class="subtext">
            <span class="age" title="2026-05-23T08:00:00 2"><a href="item?id=2">1 day ago</a></span>
        </td>
    </tr>
    </table></body></html>
""")

_NO_TITLE_HTML = textwrap.dedent("""\
    <html><body><table>
    <tr class="athing submission" id="1">
        <td class="title"><span class="titleline"></span></td>
    </tr>
    <tr><td></td></tr>
    </table></body></html>
""")

_RELATIVE_URL_HTML = textwrap.dedent("""\
    <html><body><table>
    <tr class="athing submission" id="1">
        <td class="title"><span class="titleline"><a href="item?id=99">Ask HN: Something</a></span></td>
    </tr>
    <tr>
        <td class="subtext">
            <span class="age" title="2026-05-24T12:00:00 99"><a href="item?id=99">3 hours ago</a></span>
        </td>
    </tr>
    </table></body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body><table>
    <tr class="athing submission" id="1">
        <td class="title"><span class="titleline"><a href="https://already.absolute.com/post">Already Absolute</a></span></td>
    </tr>
    <tr>
        <td class="subtext">
            <span class="age" title="2026-05-22T09:00:00 1"><a href="item?id=1">2 days ago</a></span>
        </td>
    </tr>
    </table></body></html>
""")


@pytest.fixture
def source():
    return HackerNewsSource()


# --- parse() ---

def test_parse_returns_entry_from_single_story(source):
    result = source.parse([_SINGLE_STORY_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Test Story Title"


def test_parse_expands_relative_url_to_absolute(source):
    result = source.parse([_RELATIVE_URL_HTML])
    assert result[0]["url"] == "https://news.ycombinator.com/item?id=99"


def test_parse_preserves_absolute_url_unchanged(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://already.absolute.com/post"


def test_parse_converts_date_to_iso_format(source):
    result = source.parse([_SINGLE_STORY_HTML])
    assert result[0]["date"] == "2026-05-24"


def test_parse_returns_all_stories(source):
    result = source.parse([_TWO_STORIES_HTML])
    assert len(result) == 2


def test_parse_skips_story_with_no_title(source):
    result = source.parse([_NO_TITLE_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


# --- to_dict() ---

def test_to_dict_sets_source_to_hackernews(source):
    entry = {"url": "https://example.com", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["source"] == "hackernews"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://example.com", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://example.com", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_extracts_date_from_iso_datetime():
    assert _parse_date("2026-05-24T16:31:29 123456") == "2026-05-24"


def test_parse_date_handles_datetime_without_unix_suffix():
    assert _parse_date("2026-05-23T08:00:00") == "2026-05-23"


def test_parse_date_returns_empty_string_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_string_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_HTML])
    result = source.run()
    assert result == []
