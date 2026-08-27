import textwrap

import pytest

from feedy.sources.firstround import FirstRoundSource, _parse_date


_LIST_HTML = textwrap.dedent("""\
    <html><body>
    <article class="firstound-post-item">
        <div class="flex flex-col w-full cursor-pointer card-to-responsive">
            <a href="/test-article-1/" title="Test Article One">
                <h3 class="!font-skandia-medium text-xl tracking-tight line-clamp-2 mt-2.5 mb-2.5">Test Article One</h3>
            </a>
        </div>
    </article>
    <article class="firstound-post-item">
        <div class="flex flex-col w-full cursor-pointer card-to-responsive">
            <a href="/test-article-2/" title="Test Article Two">
                <h3 class="!font-skandia-medium text-xl tracking-tight line-clamp-2 mt-2.5 mb-2.5">Test Article Two</h3>
            </a>
        </div>
    </article>
    </body></html>
""")

_ARTICLE_HTML_WITH_META = textwrap.dedent("""\
    <html><head>
    <meta property="article:published_time" content="2026-08-20T11:35:07.000Z">
    </head><body>
    <article><h1>Test Article One</h1></article>
    </body></html>
""")

_ARTICLE_HTML_WITH_TIME = textwrap.dedent("""\
    <html><body>
    <article><time datetime="2026-07-15T09:00:00.000Z">July 15, 2026</time></article>
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
    return FirstRoundSource()


# --- parse() ---

def test_parse_returns_entries_from_list(source, monkeypatch):
    """parse() should extract title and url from each article card."""
    call_count = [0]

    def mock_fetch_article_date(url):
        call_count[0] += 1
        return "2026-08-20"

    monkeypatch.setattr(source, "_fetch_article_date", mock_fetch_article_date)

    result = source.parse([_LIST_HTML])
    assert len(result) == 2
    assert result[0]["title"] == "Test Article One"
    assert result[0]["url"] == "https://review.firstround.com/test-article-1/"
    assert result[0]["date"] == "2026-08-20"
    assert result[1]["title"] == "Test Article Two"
    assert result[1]["url"] == "https://review.firstround.com/test-article-2/"
    assert call_count[0] == 2


def test_parse_deduplicates_by_url(source, monkeypatch):
    """parse() should skip duplicate URLs."""
    html = textwrap.dedent("""\
        <html><body>
        <article class="firstound-post-item">
            <a href="/same-article/" title="First">
                <h3>First</h3>
            </a>
        </article>
        <article class="firstound-post-item">
            <a href="/same-article/" title="Second">
                <h3>Second</h3>
            </a>
        </article>
        </body></html>
    """)

    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2026-08-20")

    result = source.parse([html])
    assert len(result) == 1
    assert result[0]["title"] == "First"


def test_parse_skips_article_with_no_title(source, monkeypatch):
    """parse() should skip articles with no title element."""
    html = textwrap.dedent("""\
        <html><body>
        <article class="firstound-post-item">
            <a href="/no-title/"></a>
        </article>
        </body></html>
    """)

    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2026-08-20")

    result = source.parse([html])
    assert result == []


def test_parse_skips_article_with_no_link(source, monkeypatch):
    """parse() should skip articles with no link."""
    html = textwrap.dedent("""\
        <html><body>
        <article class="firstound-post-item">
            <h3>No Link Article</h3>
        </article>
        </body></html>
    """)

    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2026-08-20")

    result = source.parse([html])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    """parse() should return empty list for empty input."""
    result = source.parse([])
    assert result == []


# --- to_dict() ---

def test_to_dict_sets_source_to_firstround(source):
    entry = {"url": "https://review.firstround.com/test/", "title": "X", "date": "2026-08-20"}
    result = source.to_dict(entry)
    assert result["source"] == "firstround"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://review.firstround.com/test/", "title": "X", "date": "2026-08-20"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://review.firstround.com/test/", "title": "X", "date": "2026-08-20"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_handles_iso_datetime_with_z():
    assert _parse_date("2026-08-20T11:35:07.000Z") == "2026-08-20"


def test_parse_date_handles_iso_datetime_with_offset():
    assert _parse_date("2026-08-20T11:35:07+00:00") == "2026-08-20"


def test_parse_date_handles_iso_date():
    assert _parse_date("2026-08-20") == "2026-08-20"


def test_parse_date_handles_slash_format():
    assert _parse_date("2026/08/20") == "2026-08-20"


def test_parse_date_handles_dot_format():
    assert _parse_date("20.08.2026") == "2026-08-20"


def test_parse_date_handles_us_format():
    assert _parse_date("08/20/2026") == "2026-08-20"


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
        <article class="firstound-post-item">
            <a href="/no-title/"></a>
        </article>
        </body></html>
    """)
    monkeypatch.setattr(source, "fetch", lambda: [html])
    monkeypatch.setattr(source, "_fetch_article_date", lambda url: "2026-08-20")
    result = source.run()
    assert result == []