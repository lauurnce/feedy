import textwrap

import pytest

from feedy.sources.sequoia_inference import SequoiaInferenceSource


_TWO_ITEMS_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <title>Inference by Sequoia</title>
      <item>
        <title>AI and the Future of Work</title>
        <link>https://inferencebysequoia.substack.com/p/ai-future-work</link>
        <pubDate>Wed, 26 Aug 2026 12:00:00 GMT</pubDate>
      </item>
      <item>
        <title>Building Foundation Models</title>
        <link>https://inferencebysequoia.substack.com/p/building-foundation-models</link>
        <pubDate>Tue, 25 Aug 2026 03:00:00 GMT</pubDate>
      </item>
    </channel></rss>
""")

_NO_TITLE_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <item>
        <link>https://inferencebysequoia.substack.com/p/no-title</link>
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
        <link>https://inferencebysequoia.substack.com/p/bad-date</link>
        <pubDate>not a date</pubDate>
      </item>
    </channel></rss>
""")

_DUPLICATE_LINK_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <item>
        <title>Duplicate Post</title>
        <link>https://inferencebysequoia.substack.com/p/duplicate</link>
        <pubDate>Wed, 26 Aug 2026 12:00:00 GMT</pubDate>
      </item>
      <item>
        <title>Duplicate Post Again</title>
        <link>https://inferencebysequoia.substack.com/p/duplicate</link>
        <pubDate>Tue, 25 Aug 2026 03:00:00 GMT</pubDate>
      </item>
    </channel></rss>
""")

_EMPTY_RSS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
    </channel></rss>
""")


@pytest.fixture
def source():
    return SequoiaInferenceSource()


def test_source_name(source):
    assert source.name == "sequoia-inference"


# --- parse() ---

def test_parse_returns_entries_from_valid_rss(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert len(result) == 2


def test_parse_extracts_title(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert result[0]["title"] == "AI and the Future of Work"
    assert result[1]["title"] == "Building Foundation Models"


def test_parse_extracts_link(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert result[0]["url"] == "https://inferencebysequoia.substack.com/p/ai-future-work"
    assert result[1]["url"] == "https://inferencebysequoia.substack.com/p/building-foundation-models"


def test_parse_parses_pubdate_to_iso(source):
    result = source.parse([_TWO_ITEMS_RSS])
    assert result[0]["date"] == "2026-08-26"
    assert result[1]["date"] == "2026-08-25"


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


def test_parse_deduplicates_by_url(source):
    result = source.parse([_DUPLICATE_LINK_RSS])
    assert len(result) == 1
    assert result[0]["title"] == "Duplicate Post"


def test_parse_handles_empty_channel(source):
    result = source.parse([_EMPTY_RSS])
    assert result == []


# --- to_dict() ---

def test_to_dict_sets_source_to_sequoia_inference(source):
    entry = {"url": "https://inferencebysequoia.substack.com/p/x", "title": "X", "date": "2026-08-26"}
    result = source.to_dict(entry)
    assert result["source"] == "sequoia-inference"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://inferencebysequoia.substack.com/p/x", "title": "X", "date": "2026-08-26"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://inferencebysequoia.substack.com/p/x", "title": "Post Title", "date": "2026-08-26"}
    result = source.to_dict(entry)
    assert result["url"] == "https://inferencebysequoia.substack.com/p/x"
    assert result["title"] == "Post Title"


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_RSS])
    result = source.run()
    assert result == []