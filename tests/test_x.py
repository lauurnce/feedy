import textwrap

import pytest
from feedy.sources.x import XSource


@pytest.fixture
def source():
    return XSource()


def test_source_name(source):
    assert source.name == "x"


_TWO_CARDS_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/en/blog/api-v3-launch/">
        <time datetime="2026-04-14">Apr 14, 2026</time>
        <h3>Launching the X API v3</h3>
    </a>
    <a href="/en/blog/rate-limit-changes/">
        <time datetime="2026-03-25">Mar 25, 2026</time>
        <h3>Rate limit changes for developers</h3>
    </a>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert len(result) == 2


def test_parse_extracts_title(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["title"] == "Launching the X API v3"
    assert result[1]["title"] == "Rate limit changes for developers"


def test_parse_expands_relative_url(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["url"] == "https://developer.x.com/en/blog/api-v3-launch/"
    assert result[1]["url"] == "https://developer.x.com/en/blog/rate-limit-changes/"


def test_parse_parses_datetime_attr_to_iso(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["date"] == "2026-04-14"
    assert result[1]["date"] == "2026-03-25"


_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <a href="https://developer.x.com/en/blog/absolute/">
        <time datetime="2026-01-01">Jan 1, 2026</time>
        <h3>Absolute URL Post</h3>
    </a>
    </body></html>
""")

_TEXT_DATE_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/en/blog/text-date/">
        <time>Feb 9, 2026</time>
        <h3>Text Date Post</h3>
    </a>
    </body></html>
""")

_NO_TITLE_CARD_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/en/blog/no-title/">
        <time datetime="2026-01-01">Jan 1, 2026</time>
    </a>
    </body></html>
""")

_NO_DATE_CARD_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/en/blog/no-date/">
        <h3>No Date Post</h3>
    </a>
    </body></html>
""")


def test_parse_preserves_absolute_url(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://developer.x.com/en/blog/absolute/"


def test_parse_parses_visible_text_date_to_iso(source):
    result = source.parse([_TEXT_DATE_HTML])
    assert result[0]["date"] == "2026-02-09"


def test_parse_empty_date_on_missing_time(source):
    result = source.parse([_NO_DATE_CARD_HTML])
    assert result[0]["date"] == ""


def test_parse_skips_card_with_no_title(source):
    result = source.parse([_NO_TITLE_CARD_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_to_dict_sets_source_to_x(source):
    entry = {"url": "https://developer.x.com/en/blog/x/", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["source"] == "x"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://developer.x.com/en/blog/x/", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://developer.x.com/en/blog/x/", "title": "Post Title", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["url"] == "https://developer.x.com/en/blog/x/"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_CARD_HTML])
    result = source.run()
    assert result == []
