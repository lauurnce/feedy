import pytest
from feedy.sources.meta import MetaSource


@pytest.fixture
def source():
    return MetaSource()


def test_source_name(source):
    assert source.name == "meta"


import textwrap

_TWO_CARDS_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/blog/post/2026/04/14/threads-api/">
        <h6>APRIL 14, 2026</h6>
        <h3>What's new in the Threads API</h3>
    </a>
    <a href="/blog/post/2026/03/25/marketing-api/">
        <h6>MARCH 25, 2026</h6>
        <h3>Marketing API Updates</h3>
    </a>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert len(result) == 2


def test_parse_extracts_title(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["title"] == "What's new in the Threads API"
    assert result[1]["title"] == "Marketing API Updates"


def test_parse_expands_relative_url(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["url"] == "https://developers.facebook.com/blog/post/2026/04/14/threads-api/"
    assert result[1]["url"] == "https://developers.facebook.com/blog/post/2026/03/25/marketing-api/"


def test_parse_parses_date_to_iso(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["date"] == "2026-04-14"
    assert result[1]["date"] == "2026-03-25"
