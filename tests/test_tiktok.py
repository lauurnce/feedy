import textwrap

import pytest
from feedy.sources.tiktok import TikTokSource


@pytest.fixture
def source():
    return TikTokSource()


def test_source_name(source):
    assert source.name == "tiktok"


_TWO_CARDS_HTML = textwrap.dedent("""\
    <html><body>
    <a data-e2e="CardContainer" href="/blog/first-post">
        <span data-e2e="TUXText">First Post Title</span>
        <span data-e2e="TUXText">Description of first post.</span>
    </a>
    <a data-e2e="CardContainer" href="/blog/second-post">
        <span data-e2e="TUXText">Second Post Title</span>
        <span data-e2e="TUXText">Description of second post.</span>
    </a>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert len(result) == 2


def test_parse_extracts_title_from_first_tux_text(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["title"] == "First Post Title"
    assert result[1]["title"] == "Second Post Title"


def test_parse_expands_relative_url(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["url"] == "https://developers.tiktok.com/blog/first-post"
    assert result[1]["url"] == "https://developers.tiktok.com/blog/second-post"


def test_parse_sets_empty_date(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["date"] == ""


_NO_TITLE_CARD_HTML = textwrap.dedent("""\
    <html><body>
    <a data-e2e="CardContainer" href="/blog/no-title">
    </a>
    </body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <a data-e2e="CardContainer" href="https://developers.tiktok.com/blog/absolute">
        <span data-e2e="TUXText">Absolute URL Post</span>
    </a>
    </body></html>
""")


def test_parse_skips_card_with_no_title(source):
    result = source.parse([_NO_TITLE_CARD_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_preserves_absolute_url_unchanged(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://developers.tiktok.com/blog/absolute"


def test_to_dict_sets_source_to_tiktok(source):
    entry = {"url": "https://developers.tiktok.com/blog/x", "title": "X", "date": ""}
    result = source.to_dict(entry)
    assert result["source"] == "tiktok"


def test_to_dict_sets_empty_date_and_summary(source):
    entry = {"url": "https://developers.tiktok.com/blog/x", "title": "X", "date": ""}
    result = source.to_dict(entry)
    assert result["date"] == ""
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://developers.tiktok.com/blog/x", "title": "Post Title", "date": ""}
    result = source.to_dict(entry)
    assert result["url"] == "https://developers.tiktok.com/blog/x"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_CARD_HTML])
    result = source.run()
    assert result == []
