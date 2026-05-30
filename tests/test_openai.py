import textwrap

import pytest
from feedy.sources.openai import OpenAISource


@pytest.fixture
def source():
    return OpenAISource()


def test_source_name(source):
    assert source.name == "openai"


# Mirrors the live openai.com/news/rss.xml feed (the HTML page is bot-blocked).
_TWO_ITEMS_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <title>OpenAI News</title>
      <item>
        <title>A new embeddings model</title>
        <link>https://openai.com/index/new-embeddings-model</link>
        <pubDate>Wed, 14 Apr 2026 12:00:00 GMT</pubDate>
      </item>
      <item>
        <title>Structured outputs in the API</title>
        <link>https://openai.com/index/structured-outputs</link>
        <pubDate>Wed, 25 Mar 2026 03:00:00 GMT</pubDate>
      </item>
    </channel></rss>
""")


def test_parse_returns_entries_from_valid_rss(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert len(result) == 2


def test_parse_extracts_title(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert result[0]["title"] == "A new embeddings model"
    assert result[1]["title"] == "Structured outputs in the API"


def test_parse_extracts_link(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert result[0]["url"] == "https://openai.com/index/new-embeddings-model"
    assert result[1]["url"] == "https://openai.com/index/structured-outputs"


def test_parse_parses_pubdate_to_iso(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert result[0]["date"] == "2026-04-14"
    assert result[1]["date"] == "2026-03-25"


_NO_TITLE_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <item>
        <link>https://openai.com/index/no-title</link>
        <pubDate>Thu, 01 Jan 2026 00:00:00 GMT</pubDate>
      </item>
    </channel></rss>
""")

_NO_LINK_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <item>
        <title>No Link Post</title>
        <pubDate>Thu, 01 Jan 2026 00:00:00 GMT</pubDate>
      </item>
    </channel></rss>
""")

_BAD_DATE_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <item>
        <title>Bad Date Post</title>
        <link>https://openai.com/index/bad-date</link>
        <pubDate>not a date</pubDate>
      </item>
    </channel></rss>
""")


def test_parse_skips_item_missing_title(source):
    result = source.parse([_NO_TITLE_RSS])
    assert result == []


def test_parse_skips_item_missing_link(source):
    result = source.parse([_NO_LINK_RSS])
    assert result == []


def test_parse_empty_date_on_bad_pubdate(source):
    result = source.parse([_BAD_DATE_RSS])
    assert result[0]["date"] == ""


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_parse_returns_empty_for_malformed_xml(source):
    result = source.parse(["<not valid xml"])
    assert result == []


def test_to_dict_sets_source_to_openai(source):
    entry = {"url": "https://openai.com/index/x", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["source"] == "openai"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://openai.com/index/x", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://openai.com/index/x", "title": "Post Title", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["url"] == "https://openai.com/index/x"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_RSS])
    result = source.run()
    assert result == []
