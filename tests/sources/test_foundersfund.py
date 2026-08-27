import textwrap

import pytest

from feedy.sources.foundersfund import FoundersFundSource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Founders Fund - Anatomy of Next</title>
        <item>
            <title>Anatomy of Next: Nuclear Energy</title>
            <link>https://foundersfund.com/anatomy-of-next/nuclear-energy/</link>
            <pubDate>Sat, 06 Jun 2026 10:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Hereticon: Contrarian Thoughts</title>
            <link>https://foundersfund.com/anatomy-of-next/hereticon-2026/</link>
            <pubDate>Sun, 07 Jun 2026 14:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/anatomy-of-next/essay-thoughtcrime/">Thoughtcrime: An Essay</a></h2>
        <span class="post-type">Essay</span>
        <span class="post-author">Trae Stephens</span>
        <time class="post-date" datetime="2026-06-03">June 3, 2026</time>
    </article>
    <div class="article">
        <h3><a href="/anatomy-of-next/podcast-episode/">Podcast: Building the Future</a></h3>
        <span class="format">Podcast</span>
        <span class="author">Team</span>
        <span class="date">2026-06-02</span>
    </div>
    <article class="entry">
        <h4 class="entry-title"><a href="/anatomy-of-next/long-form/">Long-form: Deep Dive</a></h4>
        <span class="type">Long-form</span>
        <div class="published">June 1, 2026</div>
    </article>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/anatomy-of-next/no-date/">Post Without Date</a></h2>
        <span class="post-type">Essay</span>
        <span class="post-author">Team</span>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return FoundersFundSource()


def test_name_property(source):
    assert source.name == "foundersfund"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "Anatomy of Next: Nuclear Energy"
    assert result[0]["url"] == "https://foundersfund.com/anatomy-of-next/nuclear-energy/"
    assert result[0]["date"] == "2026-06-06"
    assert result[1]["title"] == "Hereticon: Contrarian Thoughts"
    assert result[1]["date"] == "2026-06-07"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries_with_types_and_authors():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "Trae Stephens: [Essay] Thoughtcrime: An Essay"
    assert result[0]["url"] == "https://foundersfund.com/anatomy-of-next/essay-thoughtcrime/"
    assert result[0]["date"] == "2026-06-03"
    assert result[1]["title"] == "Team: [Podcast] Podcast: Building the Future"
    assert result[1]["date"] == "2026-06-02"
    assert result[2]["title"] == "[Long-form] Long-form: Deep Dive"
    assert result[2]["date"] == "2026-06-01"


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
    assert result[0]["title"] == "Team: [Essay] Post Without Date"


def test_parse_combines_rss_and_html(source):
    result = source.parse([_RSS_SAMPLE, _HTML_SAMPLE])
    assert len(result) == 5


def test_to_dict_normalizes_entry(source):
    entry = {"url": "https://foundersfund.com/anatomy-of-next/test/", "title": "Test", "date": "2026-06-06"}
    result = source.to_dict(entry)
    assert result["source"] == "foundersfund"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Sat, 06 Jun 2026 10:00:00 +0000") == "2026-06-06"
    assert _parse_date("Sun, 07 Jun 2026 14:00:00 GMT") == "2026-06-07"


def test_parse_date_iso():
    assert _parse_date("2026-06-06T10:00:00+00:00") == "2026-06-06"
    assert _parse_date("2026-06-06T10:00:00") == "2026-06-06"
    assert _parse_date("2026-06-06") == "2026-06-06"


def test_parse_date_month_name():
    assert _parse_date("June 6, 2026") == "2026-06-06"
    assert _parse_date("Jun 6, 2026") == "2026-06-06"
    assert _parse_date("6 June 2026") == "2026-06-06"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "Team: [Essay] Post Without Date"