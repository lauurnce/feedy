import textwrap

import pytest
from feedy.sources.anthropic import AnthropicSource


@pytest.fixture
def source():
    return AnthropicSource()


def test_source_name(source):
    assert source.name == "anthropic"


# Mirrors live anthropic.com/news: a featured card (heading) plus
# PublicationList grid cards (time + a title span with a hashed module class).
_TWO_CARDS_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/news/claude-opus-4-8">
        <h2 class="headline-4 FeaturedGrid__featuredTitle">Introducing Claude Opus 4.8</h2>
        <time>May 28, 2026</time>
    </a>
    <ul>
      <li><a href="/news/series-h">
        <div class="meta"><time>May 25, 2026</time><span>Announcements</span></div>
        <span class="PublicationList__title body-3">Anthropic raises Series H funding</span>
      </a></li>
    </ul>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert len(result) == 2


def test_parse_extracts_title(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["title"] == "Introducing Claude Opus 4.8"
    assert result[1]["title"] == "Anthropic raises Series H funding"


def test_parse_expands_relative_url(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["url"] == "https://www.anthropic.com/news/claude-opus-4-8"
    assert result[1]["url"] == "https://www.anthropic.com/news/series-h"


def test_parse_parses_time_date_to_iso(source):
    result = source.parse([_TWO_CARDS_HTML])
    assert result[0]["date"] == "2026-05-28"
    assert result[1]["date"] == "2026-05-25"


_DUP_SLUG_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/news/claude-opus-4-8">
        <h2 class="FeaturedGrid__featuredTitle">Introducing Claude Opus 4.8</h2>
        <time>May 28, 2026</time>
    </a>
    <ul><li><a href="/news/claude-opus-4-8">
        <div class="meta"><time>May 28, 2026</time></div>
        <span class="PublicationList__title">Introducing Claude Opus 4.8</span>
    </a></li></ul>
    </body></html>
""")

_NO_TITLE_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/news/no-title"><img src="x.png"/><time>Jan 1, 2026</time></a>
    </body></html>
""")

_NO_DATE_HTML = textwrap.dedent("""\
    <html><body>
    <a href="/news/no-date"><h3>No Date Post</h3></a>
    </body></html>
""")


def test_parse_dedupes_repeated_slug(source):
    result = source.parse([_DUP_SLUG_HTML])
    assert len(result) == 1
    assert result[0]["url"] == "https://www.anthropic.com/news/claude-opus-4-8"


def test_parse_skips_card_with_no_title(source):
    result = source.parse([_NO_TITLE_HTML])
    assert result == []


def test_parse_empty_date_on_missing_time(source):
    result = source.parse([_NO_DATE_HTML])
    assert result[0]["date"] == ""


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_to_dict_sets_source_to_anthropic(source):
    entry = {"url": "https://www.anthropic.com/news/x", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["source"] == "anthropic"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://www.anthropic.com/news/x", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://www.anthropic.com/news/x", "title": "Post Title", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["url"] == "https://www.anthropic.com/news/x"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_HTML])
    result = source.run()
    assert result == []
