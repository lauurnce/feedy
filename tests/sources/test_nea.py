import textwrap

import pytest

from feedy.sources.nea import NEASource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>NEA Blog</title>
        <item>
            <title>The Current: AI Stack Deep Dive</title>
            <link>https://www.nea.com/blog/ai-stack-deep-dive/</link>
            <pubDate>Tue, 02 Jun 2026 10:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Consumer Tech Trends 2026</title>
            <link>https://www.nea.com/blog/consumer-tech-2026/</link>
            <pubDate>Wed, 03 Jun 2026 15:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="blog-post">
        <h2 class="post-title"><a href="/blog/portfolio-news-startup/">Portfolio News: Startup Raises Series C</a></h2>
        <span class="series">The Current</span>
        <time class="post-date" datetime="2026-05-31">May 31, 2026</time>
    </article>
    <div class="article-card">
        <h3><a href="/the-current/enterprise-ai/">Enterprise AI Adoption</a></h3>
        <span class="series-name">The Current</span>
        <span class="date">2026-05-29</span>
    </div>
    <article class="entry">
        <h4 class="entry-title"><a href="/blog/venture-pulse/">Venture Pulse Q2 2026</a></h4>
        <span class="category">Market Analysis</span>
        <div class="published">May 28, 2026</div>
    </article>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="blog-post">
        <h2 class="post-title"><a href="/blog/no-date/">Post Without Date</a></h2>
        <span class="series">The Current</span>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return NEASource()


def test_name_property(source):
    assert source.name == "nea"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "The Current: AI Stack Deep Dive"
    assert result[0]["url"] == "https://www.nea.com/blog/ai-stack-deep-dive/"
    assert result[0]["date"] == "2026-06-02"
    assert result[1]["title"] == "Consumer Tech Trends 2026"
    assert result[1]["date"] == "2026-06-03"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries_with_series():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "[The Current] Portfolio News: Startup Raises Series C"
    assert result[0]["url"] == "https://www.nea.com/blog/portfolio-news-startup/"
    assert result[0]["date"] == "2026-05-31"
    assert result[1]["title"] == "[The Current] Enterprise AI Adoption"
    assert result[1]["date"] == "2026-05-29"
    assert result[2]["title"] == "[Market Analysis] Venture Pulse Q2 2026"
    assert result[2]["date"] == "2026-05-28"


def test_parse_html_deduplicates():
    seen = set()
    _parse_html(_HTML_SAMPLE, seen)
    result = _parse_html(_HTML_SAMPLE, seen)
    assert result == []


def test_parse_html_handles_missing_date():
    seen = set()
    result = _parse_html(_HTML_NO_DATE, seen)
    assert len(result) == 1
    assert result[0]["date"] == ""
    assert result[0]["title"] == "[The Current] Post Without Date"


def test_parse_combines_rss_and_html(source):
    result = source.parse([_RSS_SAMPLE, _HTML_SAMPLE])
    assert len(result) == 5


def test_to_dict_normalizes_entry(source):
    entry = {"url": "https://www.nea.com/blog/test/", "title": "Test", "date": "2026-06-02"}
    result = source.to_dict(entry)
    assert result["source"] == "nea"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Tue, 02 Jun 2026 10:00:00 +0000") == "2026-06-02"
    assert _parse_date("Wed, 03 Jun 2026 15:00:00 GMT") == "2026-06-03"


def test_parse_date_iso():
    assert _parse_date("2026-06-02T10:00:00+00:00") == "2026-06-02"
    assert _parse_date("2026-06-02T10:00:00") == "2026-06-02"
    assert _parse_date("2026-06-02") == "2026-06-02"


def test_parse_date_month_name():
    assert _parse_date("June 2, 2026") == "2026-06-02"
    assert _parse_date("Jun 2, 2026") == "2026-06-02"
    assert _parse_date("2 June 2026") == "2026-06-02"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "[The Current] Post Without Date"