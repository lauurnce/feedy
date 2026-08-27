import textwrap

import pytest

from feedy.sources.lightspeed import LightspeedSource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Lightspeed Stories</title>
        <item>
            <title>Founder Story: Building a Unicorn</title>
            <link>https://lsvp.com/stories/founder-story-unicorn/</link>
            <pubDate>Wed, 26 May 2026 09:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Partner Perspective: AI in 2026</title>
            <link>https://lsvp.com/stories/partner-perspective-ai/</link>
            <pubDate>Thu, 27 May 2026 11:30:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2 class="story-title"><a href="/stories/industry-insights/">Industry Insights: Cloud Computing</a></h2>
        <time class="story-date" datetime="2026-05-22">May 22, 2026</time>
    </article>
    <div class="post-card">
        <h3><a href="/stories/investment-announcement/">New Investment: DataCorp</a></h3>
        <span class="date">2026-05-20</span>
    </div>
    <article class="entry">
        <h4 class="entry-title"><a href="/stories/founder-journey/">Founder Journey: From Garage to IPO</a></h4>
        <div class="published">2026-05-18</div>
    </article>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="story-card">
        <h2 class="story-title"><a href="/stories/no-date/">Story Without Date</a></h2>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return LightspeedSource()


def test_name_property(source):
    assert source.name == "lightspeed"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "Founder Story: Building a Unicorn"
    assert result[0]["url"] == "https://lsvp.com/stories/founder-story-unicorn/"
    assert result[0]["date"] == "2026-05-26"
    assert result[1]["title"] == "Partner Perspective: AI in 2026"
    assert result[1]["date"] == "2026-05-27"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "Industry Insights: Cloud Computing"
    assert result[0]["url"] == "https://lsvp.com/stories/industry-insights/"
    assert result[0]["date"] == "2026-05-22"
    assert result[1]["title"] == "New Investment: DataCorp"
    assert result[1]["date"] == "2026-05-20"
    assert result[2]["title"] == "Founder Journey: From Garage to IPO"
    assert result[2]["date"] == "2026-05-18"


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
    entry = {"url": "https://lsvp.com/stories/test/", "title": "Test", "date": "2026-05-26"}
    result = source.to_dict(entry)
    assert result["source"] == "lightspeed"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Wed, 26 May 2026 09:00:00 +0000") == "2026-05-26"
    assert _parse_date("Thu, 27 May 2026 11:30:00 GMT") == "2026-05-27"


def test_parse_date_iso():
    assert _parse_date("2026-05-26T09:00:00+00:00") == "2026-05-26"
    assert _parse_date("2026-05-26T09:00:00") == "2026-05-26"
    assert _parse_date("2026-05-26") == "2026-05-26"


def test_parse_date_month_name():
    assert _parse_date("May 26, 2026") == "2026-05-26"
    assert _parse_date("May 26 2026") == "2026-05-26"
    assert _parse_date("26 May 2026") == "2026-05-26"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "Story Without Date"