import textwrap

import pytest

from feedy.sources.sequoia import SequoiaSource, _parse_date


_SINGLE_STORY_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="/stories/test-story">Test Story Title</a></h2>
        <time datetime="2026-08-26T10:00:00Z">Aug 26, 2026</time>
    </article>
    </body></html>
""")

_TWO_STORIES_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="/stories/first-story">First Story</a></h2>
        <time datetime="2026-08-26T10:00:00Z">Aug 26, 2026</time>
    </article>
    <article class="story-card">
        <h3><a href="/stories/second-story">Second Story</a></h3>
        <time datetime="2026-08-25T10:00:00Z">Aug 25, 2026</time>
    </article>
    </body></html>
""")

_NO_TITLE_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="/stories/no-title"></a></h2>
        <time datetime="2026-08-26T10:00:00Z">Aug 26, 2026</time>
    </article>
    </body></html>
""")

_RELATIVE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="/stories/relative">Relative URL Story</a></h2>
        <time datetime="2026-08-24T10:00:00Z">Aug 24, 2026</time>
    </article>
    </body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="https://sequoiacap.com/stories/absolute">Absolute URL Story</a></h2>
        <time datetime="2026-08-23T10:00:00Z">Aug 23, 2026</time>
    </article>
    </body></html>
""")

_DUPLICATE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="/stories/duplicate">Duplicate Story</a></h2>
        <time datetime="2026-08-26T10:00:00Z">Aug 26, 2026</time>
    </article>
    <article class="story-card">
        <h3><a href="/stories/duplicate">Duplicate Story Again</a></h3>
        <time datetime="2026-08-25T10:00:00Z">Aug 25, 2026</time>
    </article>
    </body></html>
""")

_ALTERNATE_SELECTORS_HTML = textwrap.dedent("""\
    <html><body>
    <div class="story-card">
        <a href="/stories/alt-selectors" class="story-title">Alt Selectors Story</a>
        <span class="date">Aug 22, 2026</span>
    </div>
    </body></html>
""")

_NO_DATE_HTML = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2><a href="/stories/no-date">No Date Story</a></h2>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return SequoiaSource()


# --- parse() ---

def test_parse_returns_entry_from_single_story(source):
    result = source.parse([_SINGLE_STORY_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Test Story Title"


def test_parse_expands_relative_url_to_absolute(source):
    result = source.parse([_RELATIVE_URL_HTML])
    assert result[0]["url"] == "https://sequoiacap.com/stories/relative"


def test_parse_preserves_absolute_url_unchanged(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://sequoiacap.com/stories/absolute"


def test_parse_converts_date_to_iso_format(source):
    result = source.parse([_SINGLE_STORY_HTML])
    assert result[0]["date"] == "2026-08-26"


def test_parse_returns_all_stories(source):
    result = source.parse([_TWO_STORIES_HTML])
    assert len(result) == 2


def test_parse_skips_story_with_no_title(source):
    result = source.parse([_NO_TITLE_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_deduplicates_by_url(source):
    result = source.parse([_DUPLICATE_URL_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Duplicate Story"


def test_parse_works_with_alternate_selectors(source):
    result = source.parse([_ALTERNATE_SELECTORS_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Alt Selectors Story"
    assert result[0]["url"] == "https://sequoiacap.com/stories/alt-selectors"
    assert result[0]["date"] == "2026-08-22"


def test_parse_handles_missing_date_gracefully(source):
    result = source.parse([_NO_DATE_HTML])
    assert len(result) == 1
    assert result[0]["date"] == ""


# --- to_dict() ---

def test_to_dict_sets_source_to_sequoia(source):
    entry = {"url": "https://sequoiacap.com/stories/x", "title": "X", "date": "2026-08-26"}
    result = source.to_dict(entry)
    assert result["source"] == "sequoia"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://sequoiacap.com/stories/x", "title": "X", "date": "2026-08-26"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://sequoiacap.com/stories/x", "title": "Post Title", "date": "2026-08-26"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_handles_iso_datetime():
    assert _parse_date("2026-08-26T10:00:00Z") == "2026-08-26"
    assert _parse_date("2026-08-26T10:00:00+00:00") == "2026-08-26"


def test_parse_date_handles_month_day_year_format():
    assert _parse_date("Aug 26, 2026") == "2026-08-26"
    assert _parse_date("August 26, 2026") == "2026-08-26"


def test_parse_date_handles_day_month_year_format():
    assert _parse_date("26 Aug 2026") == "2026-08-26"
    assert _parse_date("26 August 2026") == "2026-08-26"


def test_parse_date_handles_iso_date_format():
    assert _parse_date("2026-08-26") == "2026-08-26"


def test_parse_date_returns_empty_string_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_string_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_HTML])
    result = source.run()
    assert result == []