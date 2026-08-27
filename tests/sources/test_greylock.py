import textwrap

import pytest

from feedy.sources.greylock import GreylockSource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Greylock Blog</title>
        <item>
            <title>Building AI-First Companies</title>
            <link>https://greylock.com/blog/building-ai-first-companies/</link>
            <pubDate>Mon, 24 May 2026 10:30:00 +0000</pubDate>
        </item>
        <item>
            <title>Portfolio News: Acme Corp Raises Series B</title>
            <link>https://greylock.com/blog/portfolio-news/acme-series-b/</link>
            <pubDate>Tue, 25 May 2026 14:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/blog/greymatter-episode-1/">Greymatter Podcast: Episode 1</a></h2>
        <time class="post-date" datetime="2026-05-20">May 20, 2026</time>
    </article>
    <article class="post">
        <h2 class="post-title"><a href="/blog/firm-news/new-partner/">Welcome New Partner</a></h2>
        <time class="post-date" datetime="2026-05-18">May 18, 2026</time>
    </article>
    <div class="story-card">
        <h3><a href="/change-agents/leading-through-change/">Leading Through Change</a></h3>
        <span class="date">2026-05-15</span>
    </div>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/blog/no-date-post/">Post Without Date</a></h2>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return GreylockSource()


def test_name_property(source):
    assert source.name == "greylock"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "Building AI-First Companies"
    assert result[0]["url"] == "https://greylock.com/blog/building-ai-first-companies/"
    assert result[0]["date"] == "2026-05-24"
    assert result[1]["title"] == "Portfolio News: Acme Corp Raises Series B"
    assert result[1]["date"] == "2026-05-25"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "Greymatter Podcast: Episode 1"
    assert result[0]["url"] == "https://greylock.com/blog/greymatter-episode-1/"
    assert result[0]["date"] == "2026-05-20"
    assert result[1]["title"] == "Welcome New Partner"
    assert result[1]["date"] == "2026-05-18"
    assert result[2]["title"] == "Leading Through Change"
    assert result[2]["date"] == "2026-05-15"


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


def test_parse_combines_rss_and_html(source):
    result = source.parse([_RSS_SAMPLE, _HTML_SAMPLE])
    assert len(result) == 5


def test_to_dict_normalizes_entry(source):
    entry = {"url": "https://greylock.com/blog/test/", "title": "Test", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["source"] == "greylock"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Mon, 24 May 2026 10:30:00 +0000") == "2026-05-24"
    assert _parse_date("Tue, 25 May 2026 14:00:00 GMT") == "2026-05-25"


def test_parse_date_iso():
    assert _parse_date("2026-05-24T10:30:00+00:00") == "2026-05-24"
    assert _parse_date("2026-05-24T10:30:00") == "2026-05-24"
    assert _parse_date("2026-05-24") == "2026-05-24"


def test_parse_date_month_name():
    assert _parse_date("May 24, 2026") == "2026-05-24"
    assert _parse_date("May 24 2026") == "2026-05-24"
    assert _parse_date("24 May 2026") == "2026-05-24"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "Post Without Date"