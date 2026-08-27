import textwrap

import pytest

from feedy.sources.index import IndexSource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Index Ventures Perspectives</title>
        <item>
            <title>The Future of Fintech</title>
            <link>https://www.indexventures.com/perspectives/future-of-fintech/</link>
            <pubDate>Sun, 30 May 2026 12:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Open Source Spotlight: New Project</title>
            <link>https://www.indexventures.com/opensource/new-project/</link>
            <pubDate>Mon, 31 May 2026 14:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="perspective">
        <h2 class="perspective-title"><a href="/perspectives/ai-infrastructure/">Building AI Infrastructure</a></h2>
        <span class="perspective-category">Insights</span>
        <time class="post-date" datetime="2026-05-28">May 28, 2026</time>
    </article>
    <div class="article-card">
        <h3><a href="/perspectives/news/fund-announcement/">New Fund Announcement</a></h3>
        <span class="category">News</span>
        <span class="date">2026-05-27</span>
    </div>
    <article class="entry">
        <h4 class="article-title"><a href="/opensource/ml-framework/">Open Source ML Framework</a></h4>
        <span class="tag">Open Source</span>
        <div class="published">May 26, 2026</div>
    </article>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="perspective">
        <h2 class="perspective-title"><a href="/perspectives/no-date/">Perspective Without Date</a></h2>
        <span class="perspective-category">Insights</span>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return IndexSource()


def test_name_property(source):
    assert source.name == "index"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "The Future of Fintech"
    assert result[0]["url"] == "https://www.indexventures.com/perspectives/future-of-fintech/"
    assert result[0]["date"] == "2026-05-30"
    assert result[1]["title"] == "Open Source Spotlight: New Project"
    assert result[1]["date"] == "2026-05-31"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries_with_categories():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "[Insights] Building AI Infrastructure"
    assert result[0]["url"] == "https://www.indexventures.com/perspectives/ai-infrastructure/"
    assert result[0]["date"] == "2026-05-28"
    assert result[1]["title"] == "[News] New Fund Announcement"
    assert result[1]["date"] == "2026-05-27"
    assert result[2]["title"] == "[Open Source] Open Source ML Framework"
    assert result[2]["date"] == "2026-05-26"


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
    assert result[0]["title"] == "[Insights] Perspective Without Date"


def test_parse_combines_rss_and_html(source):
    result = source.parse([_RSS_SAMPLE, _HTML_SAMPLE])
    assert len(result) == 5


def test_to_dict_normalizes_entry(source):
    entry = {"url": "https://www.indexventures.com/perspectives/test/", "title": "Test", "date": "2026-05-30"}
    result = source.to_dict(entry)
    assert result["source"] == "index"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Sun, 30 May 2026 12:00:00 +0000") == "2026-05-30"
    assert _parse_date("Mon, 31 May 2026 14:00:00 GMT") == "2026-05-31"


def test_parse_date_iso():
    assert _parse_date("2026-05-30T12:00:00+00:00") == "2026-05-30"
    assert _parse_date("2026-05-30T12:00:00") == "2026-05-30"
    assert _parse_date("2026-05-30") == "2026-05-30"


def test_parse_date_month_name():
    assert _parse_date("May 30, 2026") == "2026-05-30"
    assert _parse_date("May 30 2026") == "2026-05-30"
    assert _parse_date("30 May 2026") == "2026-05-30"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "[Insights] Perspective Without Date"