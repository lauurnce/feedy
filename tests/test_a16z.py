import textwrap

import pytest

from feedy.sources.a16z import A16ZSource, _parse_date


_SINGLE_ARTICLE_HTML = textwrap.dedent("""\
    <html><body>
    <article>
        <h2><a href="/news-content/test-article">Test Article Title</a></h2>
        <time datetime="2026-05-24T16:31:29+00:00">May 24, 2026</time>
    </article>
    </body></html>
""")

_TWO_ARTICLES_HTML = textwrap.dedent("""\
    <html><body>
    <article class="post-card">
        <h3><a href="/news-content/first">First Article</a></h3>
        <div class="date">May 1, 2026</div>
    </article>
    <article class="post-card">
        <h2><a href="https://a16z.com/news-content/second">Second Article</a></h2>
        <time datetime="2026-04-15T10:00:00Z">April 15, 2026</time>
    </article>
    </body></html>
""")

_NO_TITLE_HTML = textwrap.dedent("""\
    <html><body>
    <article>
        <time datetime="2026-05-24">May 24, 2026</time>
    </article>
    </body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <article>
        <h2><a href="https://example.com/external">External Article</a></h2>
    </article>
    </body></html>
""")

_DUPLICATE_URLS_HTML = textwrap.dedent("""\
    <html><body>
    <article>
        <h2><a href="/news-content/duplicate">Duplicate Article</a></h2>
    </article>
    <article>
        <h3><a href="/news-content/duplicate">Duplicate Article</a></h3>
    </article>
    </body></html>
""")

_CARD_SELECTOR_HTML = textwrap.dedent("""\
    <html><body>
    <div class="post-card">
        <h3 class="post-title"><a href="/news-content/card-article">Card Article</a></h3>
        <span class="post-date">Jun 1, 2026</span>
    </div>
    </body></html>
""")


@pytest.fixture
def source():
    return A16ZSource()


# --- parse() ---

def test_parse_returns_entry_from_single_article(source):
    result = source.parse([_SINGLE_ARTICLE_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Test Article Title"


def test_parse_expands_relative_url_to_absolute(source):
    result = source.parse([_SINGLE_ARTICLE_HTML])
    assert result[0]["url"] == "https://a16z.com/news-content/test-article"


def test_parse_preserves_absolute_url_unchanged(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://example.com/external"


def test_parse_converts_date_to_iso_format(source):
    result = source.parse([_SINGLE_ARTICLE_HTML])
    assert result[0]["date"] == "2026-05-24"


def test_parse_returns_all_articles(source):
    result = source.parse([_TWO_ARTICLES_HTML])
    assert len(result) == 2


def test_parse_skips_article_with_no_title(source):
    result = source.parse([_NO_TITLE_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_deduplicates_by_url(source):
    result = source.parse([_DUPLICATE_URLS_HTML])
    assert len(result) == 1


def test_parse_works_with_card_selectors(source):
    result = source.parse([_CARD_SELECTOR_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Card Article"
    assert result[0]["url"] == "https://a16z.com/news-content/card-article"


# --- to_dict() ---

def test_to_dict_sets_source_to_a16z(source):
    entry = {"url": "https://a16z.com/x", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["source"] == "a16z"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://a16z.com/x", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://a16z.com/x", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_handles_iso_datetime_with_timezone():
    assert _parse_date("2026-05-24T16:31:29+00:00") == "2026-05-24"


def test_parse_date_handles_iso_datetime_zulu():
    assert _parse_date("2026-04-15T10:00:00Z") == "2026-04-15"


def test_parse_date_handles_iso_date_only():
    assert _parse_date("2026-05-24") == "2026-05-24"


def test_parse_date_handles_month_day_year_format():
    assert _parse_date("May 24, 2026") == "2026-05-24"


def test_parse_date_handles_abbreviated_month():
    assert _parse_date("May 1, 2026") == "2026-05-01"


def test_parse_date_handles_day_month_year_format():
    assert _parse_date("24 May 2026") == "2026-05-24"


def test_parse_date_returns_empty_string_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_string_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_HTML])
    result = source.run()
    assert result == []