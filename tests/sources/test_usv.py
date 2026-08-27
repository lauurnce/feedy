import textwrap

import pytest

from feedy.sources.usv import USVSource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>USV Blog</title>
        <item>
            <title>Fred Wilson: The Future of Crypto</title>
            <link>https://blog.usv.com/future-of-crypto/</link>
            <pubDate>Fri, 28 May 2026 08:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Albert Wenger: AI and Society</title>
            <link>https://blog.usv.com/ai-and-society/</link>
            <pubDate>Sat, 29 May 2026 10:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/writing/2026/05/25/venture-capital-trends/">Venture Capital Trends 2026</a></h2>
        <span class="post-author">Fred Wilson</span>
        <time class="post-date" datetime="2026-05-25">May 25, 2026</time>
    </article>
    <article class="writing-post">
        <h3><a href="/writing/2026/05/24/climate-tech/">Climate Tech Investment Thesis</a></h3>
        <div class="author">Albert Wenger</div>
        <span class="date">2026-05-24</span>
    </article>
    <div class="entry">
        <h4 class="entry-title"><a href="/writing/2026/05/23/network-effects/">Network Effects in Web3</a></h4>
        <span class="published">May 23, 2026</span>
    </div>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/writing/no-date/">Post Without Date</a></h2>
        <span class="post-author">Nick Grossman</span>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return USVSource()


def test_name_property(source):
    assert source.name == "usv"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "Fred Wilson: The Future of Crypto"
    assert result[0]["url"] == "https://blog.usv.com/future-of-crypto/"
    assert result[0]["date"] == "2026-05-28"
    assert result[1]["title"] == "Albert Wenger: AI and Society"
    assert result[1]["date"] == "2026-05-29"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries_with_authors():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "Fred Wilson: Venture Capital Trends 2026"
    assert result[0]["url"] == "https://www.usv.com/writing/2026/05/25/venture-capital-trends/"
    assert result[0]["date"] == "2026-05-25"
    assert result[1]["title"] == "Albert Wenger: Climate Tech Investment Thesis"
    assert result[1]["date"] == "2026-05-24"
    assert result[2]["title"] == "Network Effects in Web3"
    assert result[2]["date"] == "2026-05-23"


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
    assert result[0]["title"] == "Nick Grossman: Post Without Date"


def test_parse_combines_rss_and_html(source):
    result = source.parse([_RSS_SAMPLE, _HTML_SAMPLE])
    assert len(result) == 5


def test_to_dict_normalizes_entry(source):
    entry = {"url": "https://www.usv.com/writing/test/", "title": "Test", "date": "2026-05-28"}
    result = source.to_dict(entry)
    assert result["source"] == "usv"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Fri, 28 May 2026 08:00:00 +0000") == "2026-05-28"
    assert _parse_date("Sat, 29 May 2026 10:00:00 GMT") == "2026-05-29"


def test_parse_date_iso():
    assert _parse_date("2026-05-28T08:00:00+00:00") == "2026-05-28"
    assert _parse_date("2026-05-28T08:00:00") == "2026-05-28"
    assert _parse_date("2026-05-28") == "2026-05-28"


def test_parse_date_month_name():
    assert _parse_date("May 28, 2026") == "2026-05-28"
    assert _parse_date("May 28 2026") == "2026-05-28"
    assert _parse_date("28 May 2026") == "2026-05-28"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "Nick Grossman: Post Without Date"