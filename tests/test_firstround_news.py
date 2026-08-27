import textwrap

import pytest

from feedy.sources.firstround_news import FirstRoundNewsSource, _parse_date


_LIST_HTML = textwrap.dedent("""\
    <html><body>
    <article class="article-list__item">
        <a class="link article-tile article-tile--white article-tile--with-cta-arrow" href="/news/test-article-1">
            <h2 class="heading article-tile__heading">Test Article One</h2>
        </a>
    </article>
    <article class="article-list__item">
        <a class="link article-tile article-tile--white article-tile--with-cta-arrow" href="/news/test-article-2">
            <h2 class="heading article-tile__heading">Test Article Two</h2>
        </a>
    </article>
    </body></html>
""")

_ARTICLE_HTML_WITH_TIME = textwrap.dedent("""\
    <html><body>
    <article><time datetime="2025-12-16T07:00:00.000-08:00">12.16.2025</time></article>
    </body></html>
""")

_ARTICLE_HTML_WITH_META = textwrap.dedent("""\
    <html><head>
    <meta property="article:published_time" content="2026-01-15T10:00:00.000Z">
    </head><body>
    <article><h1>Test Article</h1></article>
    </body></html>
""")

_ARTICLE_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article><h1>Test Article</h1></article>
    </body></html>
""")

_EMPTY_HTML = "<html><body></body></html>"


@pytest.fixture
def source():
    return FirstRoundNewsSource()


# --- parse() ---

def test_parse_returns_entries_from_list(source, monkeypatch):
    """parse() should extract title and url from each article card."""
    call_count = [0]

    def mock_fetch_article_date(url):
        call_count[0] += 1
        return "2025-12-16"

    monkeypatch.setattr(source, "_fetch_article_date", mock_fetch_article_date)

    result = source.parse([_LIST_HTML])
    assert len(result) == 2
    assert result[0]["title"] == "Test Article One"
    assert result[0]["url"] == "https://www.firstround.com/news/test-article-1"
    assert result[0]["date"] == "2025-12-16"
    assert result[1]["title"] == "Test Article Two"
    assert result[1]["url"] == "https://www.firstround.com/news/test-article-2"
    assert call_count[0] == 2


def test_parse_strips_news_prefix_from_title(source, monkeypatch):
    """parse() should remove 'News' prefix from title."""
    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2025-12-16")

    result = source.parse([_LIST_HTML])
    assert result[0]["title"] == "Test Article One"
    assert not result[0]["title"].startswith("News")


def test_parse_deduplicates_by_url(source, monkeypatch):
    """parse() should skip duplicate URLs."""
    html = textwrap.dedent("""\
        <html><body>
        <article class="article-list__item">
            <a class="link article-tile" href="/news/same-article">
                <h2 class="heading article-tile__heading">First</h2>
            </a>
        </article>
        <article class="article-list__item">
            <a class="link article-tile" href="/news/same-article">
                <h2 class="heading article-tile__heading">Second</h2>
            </a>
        </article>
        </body></html>
    """)

    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2025-12-16")

    result = source.parse([html])
    assert len(result) == 1
    assert result[0]["title"] == "First"


def test_parse_skips_article_with_no_link(source, monkeypatch):
    """parse() should skip articles with no link."""
    html = textwrap.dedent("""\
        <html><body>
        <article class="article-list__item">
            <div>No Link Article</div>
        </article>
        </body></html>
    """)

    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2025-12-16")

    result = source.parse([html])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    """parse() should return empty list for empty input."""
    result = source.parse([])
    assert result == []


# --- to_dict() ---

def test_to_dict_sets_source_to_firstround_news(source):
    entry = {"url": "https://www.firstround.com/news/test/", "title": "X", "date": "2025-12-16"}
    result = source.to_dict(entry)
    assert result["source"] == "firstround-news"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://www.firstround.com/news/test/", "title": "X", "date": "2025-12-16"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://www.firstround.com/news/test/", "title": "X", "date": "2025-12-16"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_handles_iso_datetime_with_z():
    assert _parse_date("2026-01-15T10:00:00.000Z") == "2026-01-15"


def test_parse_date_handles_iso_datetime_with_offset():
    assert _parse_date("2025-12-16T07:00:00.000-08:00") == "2025-12-16"


def test_parse_date_handles_iso_date():
    assert _parse_date("2026-01-15") == "2026-01-15"


def test_parse_date_handles_slash_format():
    assert _parse_date("2026/01/15") == "2026-01-15"


def test_parse_date_handles_dot_format():
    assert _parse_date("15.01.2026") == "2026-01-15"


def test_parse_date_handles_us_format():
    assert _parse_date("01/15/2026") == "2026-01-15"


def test_parse_date_returns_empty_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_EMPTY_HTML])
    result = source.run()
    assert result == []


def test_run_filters_out_entry_missing_title(source, monkeypatch):
    html = textwrap.dedent("""\
        <html><body>
        <article class="article-list__item">
            <a class="link article-tile" href="/news/no-title/">
                <h2 class="heading article-tile__heading"></h2>
            </a>
        </article>
        </body></html>
    """)
    monkeypatch.setattr(source, "fetch", lambda: [html])
    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2025-12-16")
    result = source.run()
    assert result == []