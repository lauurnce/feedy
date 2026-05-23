import textwrap

import pytest

from feedy.sources.telegram import TelegramSource, _parse_date


_SINGLE_POST_HTML = textwrap.dedent("""\
    <html><body>
    <a class="dev_blog_card_link_wrap" href="/blog/test-post">
        <h4 class="dev_blog_card_title">Test Post Title</h4>
        <div class="dev_blog_card_date">May 22, 2026</div>
    </a>
    </body></html>
""")

_TWO_POSTS_HTML = textwrap.dedent("""\
    <html><body>
    <a class="dev_blog_card_link_wrap" href="/blog/first">
        <h4 class="dev_blog_card_title">First</h4>
        <div class="dev_blog_card_date">May 1, 2026</div>
    </a>
    <a class="dev_blog_card_link_wrap" href="/blog/second">
        <h4 class="dev_blog_card_title">Second</h4>
        <div class="dev_blog_card_date">April 1, 2026</div>
    </a>
    </body></html>
""")

_NO_TITLE_HTML = textwrap.dedent("""\
    <html><body>
    <a class="dev_blog_card_link_wrap" href="/blog/no-title">
        <div class="dev_blog_card_date">May 22, 2026</div>
    </a>
    </body></html>
""")

_ABSOLUTE_URL_HTML = textwrap.dedent("""\
    <html><body>
    <a class="dev_blog_card_link_wrap" href="https://telegram.org/blog/already-absolute">
        <h4 class="dev_blog_card_title">Absolute URL Post</h4>
    </a>
    </body></html>
""")


@pytest.fixture
def source():
    return TelegramSource()


# --- parse() ---

def test_parse_returns_entry_from_single_card(source):
    result = source.parse([_SINGLE_POST_HTML])
    assert len(result) == 1
    assert result[0]["title"] == "Test Post Title"


def test_parse_expands_relative_url_to_absolute(source):
    result = source.parse([_SINGLE_POST_HTML])
    assert result[0]["url"] == "https://telegram.org/blog/test-post"


def test_parse_preserves_absolute_url_unchanged(source):
    result = source.parse([_ABSOLUTE_URL_HTML])
    assert result[0]["url"] == "https://telegram.org/blog/already-absolute"


def test_parse_converts_date_to_iso_format(source):
    result = source.parse([_SINGLE_POST_HTML])
    assert result[0]["date"] == "2026-05-22"


def test_parse_returns_all_posts(source):
    result = source.parse([_TWO_POSTS_HTML])
    assert len(result) == 2


def test_parse_skips_card_with_no_title(source):
    result = source.parse([_NO_TITLE_HTML])
    assert result == []


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


# --- to_dict() ---

def test_to_dict_sets_source_to_telegram(source):
    entry = {"url": "https://telegram.org/blog/x", "title": "X", "date": "2026-05-22"}
    result = source.to_dict(entry)
    assert result["source"] == "telegram"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://telegram.org/blog/x", "title": "X", "date": "2026-05-22"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_title_date(source):
    entry = {"url": "https://telegram.org/blog/x", "title": "X", "date": "2026-05-22"}
    result = source.to_dict(entry)
    assert result["url"] == entry["url"]
    assert result["title"] == entry["title"]
    assert result["date"] == entry["date"]


# --- _parse_date() ---

def test_parse_date_handles_month_day_year_format():
    assert _parse_date("May 22, 2026") == "2026-05-22"


def test_parse_date_handles_day_month_year_format():
    assert _parse_date("22 May 2026") == "2026-05-22"


def test_parse_date_returns_empty_string_for_unknown_format():
    assert _parse_date("not a date") == ""


def test_parse_date_returns_empty_string_for_empty_input():
    assert _parse_date("") == ""


# --- run() via _is_valid() ---

def test_run_filters_out_entry_missing_url(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_HTML])
    result = source.run()
    assert result == []
