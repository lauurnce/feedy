import textwrap

import pytest

from feedy.sources.khosla import KhoslaSource, _parse_date, _parse_rss, _parse_html


_RSS_SAMPLE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Khosla Ventures Blog</title>
        <item>
            <title>Vinod Khosla: AI Will Transform Healthcare</title>
            <link>https://www.khoslaventures.com/venture-assistance-blog/ai-healthcare/</link>
            <pubDate>Thu, 04 Jun 2026 09:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Climate Tech: The Next Frontier</title>
            <link>https://www.khoslaventures.com/venture-assistance-blog/climate-tech/</link>
            <pubDate>Fri, 05 Jun 2026 11:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_HTML_SAMPLE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/venture-assistance-blog/venture-philosophy/">Venture Assistance Philosophy</a></h2>
        <span class="post-author">Vinod Khosla</span>
        <time class="post-date" datetime="2026-06-01">June 1, 2026</time>
    </article>
    <div class="blog-post">
        <h3><a href="/venture-assistance-blog/ai-investment-thesis/">AI Investment Thesis</a></h3>
        <span class="author">Vinod Khosla</span>
        <span class="date">2026-05-30</span>
    </div>
    <article class="entry">
        <h4 class="entry-title"><a href="/venture-assistance-blog/founder-advice/">Advice for Founders</a></h4>
        <div class="published">May 29, 2026</div>
    </article>
    </body></html>
""")

_HTML_NO_DATE = textwrap.dedent("""\
    <html><body>
    <article class="post">
        <h2 class="post-title"><a href="/venture-assistance-blog/no-date/">Post Without Date</a></h2>
        <span class="post-author">Vinod Khosla</span>
    </article>
    </body></html>
""")


@pytest.fixture
def source():
    return KhoslaSource()


def test_name_property(source):
    assert source.name == "khosla"


def test_parse_rss_extracts_entries():
    seen = set()
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert len(result) == 2
    assert result[0]["title"] == "Vinod Khosla: AI Will Transform Healthcare"
    assert result[0]["url"] == "https://www.khoslaventures.com/venture-assistance-blog/ai-healthcare/"
    assert result[0]["date"] == "2026-06-04"
    assert result[1]["title"] == "Climate Tech: The Next Frontier"
    assert result[1]["date"] == "2026-06-05"


def test_parse_rss_deduplicates():
    seen = set()
    _parse_rss(_RSS_SAMPLE, seen)
    result = _parse_rss(_RSS_SAMPLE, seen)
    assert result == []


def test_parse_html_extracts_entries_with_authors():
    seen = set()
    result = _parse_html(_HTML_SAMPLE, seen)
    assert len(result) == 3
    assert result[0]["title"] == "Vinod Khosla: Venture Assistance Philosophy"
    assert result[0]["url"] == "https://www.khoslaventures.com/venture-assistance-blog/venture-philosophy/"
    assert result[0]["date"] == "2026-06-01"
    assert result[1]["title"] == "Vinod Khosla: AI Investment Thesis"
    assert result[1]["date"] == "2026-05-30"
    assert result[2]["title"] == "Advice for Founders"
    assert result[2]["date"] == "2026-05-29"


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
    assert result[0]["title"] == "Vinod Khosla: Post Without Date"


def test_parse_combines_rss_and_html(source):
    result = source.parse([_RSS_SAMPLE, _HTML_SAMPLE])
    assert len(result) == 5


def test_to_dict_normalizes_entry(source):
    entry = {"url": "https://www.khoslaventures.com/venture-assistance-blog/test/", "title": "Test", "date": "2026-06-04"}
    result = source.to_dict(entry)
    assert result["source"] == "khosla"
    assert result["summary"] == ""
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


def test_parse_date_rfc822():
    assert _parse_date("Thu, 04 Jun 2026 09:00:00 +0000") == "2026-06-04"
    assert _parse_date("Fri, 05 Jun 2026 11:00:00 GMT") == "2026-06-05"


def test_parse_date_iso():
    assert _parse_date("2026-06-04T09:00:00+00:00") == "2026-06-04"
    assert _parse_date("2026-06-04T09:00:00") == "2026-06-04"
    assert _parse_date("2026-06-04") == "2026-06-04"


def test_parse_date_month_name():
    assert _parse_date("June 4, 2026") == "2026-06-04"
    assert _parse_date("Jun 4, 2026") == "2026-06-04"
    assert _parse_date("4 June 2026") == "2026-06-04"


def test_parse_date_invalid():
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


def test_run_filters_invalid_entries(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_HTML_NO_DATE])
    result = source.run()
    assert len(result) == 1
    assert result[0]["title"] == "Vinod Khosla: Post Without Date"