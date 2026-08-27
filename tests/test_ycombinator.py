import textwrap

import pytest

from feedy.sources.ycombinator import YCombinatorSource, _parse_date


_SINGLE_ITEM_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title><![CDATA[Test Post Title]]></title>
                <link>https://www.ycombinator.com/blog/test-post/</link>
                <pubDate>Wed, 10 Dec 2025 04:32:10 GMT</pubDate>
                <category><![CDATA[YC News]]></category>
                <description><![CDATA[Test description]]></description>
            </item>
        </channel>
    </rss>
""")

_TWO_ITEMS_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title><![CDATA[First Post]]></title>
                <link>https://www.ycombinator.com/blog/first/</link>
                <pubDate>Wed, 10 Dec 2025 04:32:10 GMT</pubDate>
            </item>
            <item>
                <title><![CDATA[Second Post]]></title>
                <link>https://www.ycombinator.com/blog/second/</link>
                <pubDate>Tue, 09 Dec 2025 10:15:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
""")

_NO_TITLE_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <link>https://www.ycombinator.com/blog/no-title/</link>
                <pubDate>Wed, 10 Dec 2025 04:32:10 GMT</pubDate>
            </item>
        </channel>
    </rss>
""")

_DUPLICATE_URL_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title><![CDATA[First Post]]></title>
                <link>https://www.ycombinator.com/blog/same/</link>
                <pubDate>Wed, 10 Dec 2025 04:32:10 GMT</pubDate>
            </item>
            <item>
                <title><![CDATA[Second Post]]></title>
                <link>https://www.ycombinator.com/blog/same/</link>
                <pubDate>Tue, 09 Dec 2025 10:15:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
""")

_EMPTY_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
        </channel>
    </rss>
""")


@pytest.fixture
def source():
    return YCombinatorSource()


# --- parse() ---

def test_parse_returns_entry_from_single_item(source):
    result = source.parse([_SINGLE_ITEM_RSS])
    assert len(result) == 1
    assert result[0]["title"] == "Test Post Title"
    assert result[0]["url"] == "https://www.ycombinator.com/blog/test-post/"


def test_parse_converts_date_to_iso_format(source):
    result = source.parse([_SINGLE_ITEM_RSS])
    assert result[0]["date"] == "2025-12-10"


def test_parse_returns_all_items(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert len(result) == 2
    assert result[0]["title"] == "First Post"
    assert result[1]["title"] == "Second Post"


def test_parse_skips_item_with_no_title(source):
    result = source.parse([_NO_TITLE_RSS])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_deduplicates_by_url(source):
    result = source.parse([_DUPLICATE_URL_RSS])
    assert len(result) == 1
    assert result[0]["title"] == "First Post"


def test_parse_empty_channel(source):
    result = source.parse([_EMPTY_RSS])
    assert result == []


# --- to_dict() ---

def test_to_dict_sets_source_to_ycombinator(source):
    entry = {"url": "https://www.ycombinator.com/blog/x", "title": "X", "date": "2025-12-10"}
    result = source.to_dict(entry)
    assert result["source"] == "ycombinator"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://www.ycombinator.com/blog/x", "title": "X", "date": "2025-12-10"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://www.ycombinator.com/blog/x", "title": "X", "date": "2025-12-10"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_rfc822_format():
    assert _parse_date("Wed, 10 Dec 2025 04:32:10 GMT") == "2025-12-10"


def test_parse_date_rfc822_with_different_day():
    assert _parse_date("Tue, 09 Dec 2025 10:15:00 GMT") == "2025-12-09"


def test_parse_date_returns_empty_string_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_string_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_RSS])
    result = source.run()
    assert result == []