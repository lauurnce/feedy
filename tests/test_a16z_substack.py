import textwrap

import pytest

from feedy.sources.a16z_substack import A16ZSubstackSource, _parse_date


_SINGLE_ITEM_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>a16z</title>
        <link>https://www.a16z.news</link>
        <item>
            <title>Test Newsletter Title</title>
            <link>https://www.a16z.news/p/test-newsletter</link>
            <pubDate>Fri, 24 May 2026 16:31:29 +0000</pubDate>
            <description>Test description</description>
        </item>
    </channel>
    </rss>
""")

_TWO_ITEMS_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>a16z</title>
        <link>https://www.a16z.news</link>
        <item>
            <title>First Newsletter</title>
            <link>https://www.a16z.news/p/first</link>
            <pubDate>Fri, 01 May 2026 10:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Second Newsletter</title>
            <link>https://www.a16z.news/p/second</link>
            <pubDate>Mon, 15 Apr 2026 08:00:00 -0400</pubDate>
        </item>
    </channel>
    </rss>
""")

_NO_TITLE_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>a16z</title>
        <link>https://www.a16z.news</link>
        <item>
            <link>https://www.a16z.news/p/no-title</link>
            <pubDate>Fri, 24 May 2026 16:31:29 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_DUPLICATE_URLS_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>a16z</title>
        <link>https://www.a16z.news</link>
        <item>
            <title>First</title>
            <link>https://www.a16z.news/p/duplicate</link>
            <pubDate>Fri, 24 May 2026 10:00:00 +0000</pubDate>
        </item>
        <item>
            <title>Second</title>
            <link>https://www.a16z.news/p/duplicate</link>
            <pubDate>Fri, 24 May 2026 12:00:00 +0000</pubDate>
        </item>
    </channel>
    </rss>
""")

_ATOM_FEED = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <title>a16z</title>
        <link href="https://www.a16z.news"/>
        <entry>
            <title>Atom Entry</title>
            <link href="https://www.a16z.news/p/atom"/>
            <updated>2026-05-24T16:31:29Z</updated>
        </entry>
    </feed>
""")


@pytest.fixture
def source():
    return A16ZSubstackSource()


# --- parse() ---

def test_parse_returns_entry_from_single_item(source):
    result = source.parse([_SINGLE_ITEM_RSS])
    assert len(result) == 1
    assert result[0]["title"] == "Test Newsletter Title"


def test_parse_extracts_url(source):
    result = source.parse([_SINGLE_ITEM_RSS])
    assert result[0]["url"] == "https://www.a16z.news/p/test-newsletter"


def test_parse_converts_rfc822_date_to_iso_format(source):
    result = source.parse([_SINGLE_ITEM_RSS])
    assert result[0]["date"] == "2026-05-24"


def test_parse_returns_all_items(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert len(result) == 2


def test_parse_skips_item_with_no_title(source):
    result = source.parse([_NO_TITLE_RSS])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_deduplicates_by_url(source):
    result = source.parse([_DUPLICATE_URLS_RSS])
    assert len(result) == 1


# --- to_dict() ---

def test_to_dict_sets_source_to_a16z_substack(source):
    entry = {"url": "https://www.a16z.news/p/x", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["source"] == "a16z-substack"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://www.a16z.news/p/x", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://www.a16z.news/p/x", "title": "X", "date": "2026-05-24"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_handles_rfc822_with_timezone_offset():
    assert _parse_date("Fri, 24 May 2026 16:31:29 +0000") == "2026-05-24"


def test_parse_date_handles_rfc822_with_named_timezone():
    assert _parse_date("Fri, 24 May 2026 16:31:29 GMT") == "2026-05-24"


def test_parse_date_handles_rfc822_without_timezone():
    assert _parse_date("Fri, 24 May 2026 16:31:29") == "2026-05-24"


def test_parse_date_handles_rfc822_day_first():
    assert _parse_date("24 May 2026 16:31:29 +0000") == "2026-05-24"


def test_parse_date_handles_iso_datetime_with_timezone():
    assert _parse_date("2026-05-24T16:31:29+00:00") == "2026-05-24"


def test_parse_date_handles_iso_datetime_zulu():
    assert _parse_date("2026-05-24T16:31:29Z") == "2026-05-24"


def test_parse_date_handles_iso_date_only():
    assert _parse_date("2026-05-24") == "2026-05-24"


def test_parse_date_returns_empty_string_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_string_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_RSS])
    result = source.run()
    assert result == []