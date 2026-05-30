import textwrap

import pytest
from feedy.sources.x import XSource


@pytest.fixture
def source():
    return XSource()


def test_source_name(source):
    assert source.name == "x"


# Mirrors the live docs.x.com/changelog Mintlify "update" component:
# a row holds an update-label (date) column and an update-content column (h3 title).
_TWO_ENTRIES_HTML = textwrap.dedent("""\
    <html><body>
    <div class="update-row">
      <div><div data-component-part="update-label">Apr 14, 2026</div>
           <div data-component-part="update-description">X API v2</div></div>
      <div><div class="prose-sm" data-component-part="update-content">
           <h3 id="api-v3-launch">​Launching the X API v3</h3>
           <span>body text</span></div></div>
    </div>
    <div class="update-row">
      <div><div data-component-part="update-label">Mar 25, 2026</div></div>
      <div><div class="prose-sm" data-component-part="update-content">
           <h3 id="rate-limit-changes">​Rate limit changes for developers</h3>
           <span>body</span></div></div>
    </div>
    </body></html>
""")


def test_parse_returns_entries_from_valid_html(source):
    result = source.parse([_TWO_ENTRIES_HTML])
    assert len(result) == 2


def test_parse_extracts_title_stripping_zero_width(source):
    result = source.parse([_TWO_ENTRIES_HTML])
    assert result[0]["title"] == "Launching the X API v3"
    assert result[1]["title"] == "Rate limit changes for developers"


def test_parse_builds_changelog_anchor_url(source):
    result = source.parse([_TWO_ENTRIES_HTML])
    assert result[0]["url"] == "https://docs.x.com/changelog#api-v3-launch"
    assert result[1]["url"] == "https://docs.x.com/changelog#rate-limit-changes"


def test_parse_parses_label_date_to_iso(source):
    result = source.parse([_TWO_ENTRIES_HTML])
    assert result[0]["date"] == "2026-04-14"
    assert result[1]["date"] == "2026-03-25"


_NO_TITLE_HTML = textwrap.dedent("""\
    <html><body>
    <div class="update-row">
      <div><div data-component-part="update-label">Jan 1, 2026</div></div>
      <div><div data-component-part="update-content"><span>no heading here</span></div></div>
    </div>
    </body></html>
""")

_NO_DATE_HTML = textwrap.dedent("""\
    <html><body>
    <div class="update-row">
      <div><div data-component-part="update-content">
           <h3 id="no-date">​No Date Entry</h3></div></div>
    </div>
    </body></html>
""")


def test_parse_skips_content_with_no_title(source):
    result = source.parse([_NO_TITLE_HTML])
    assert result == []


def test_parse_empty_date_on_missing_label(source):
    result = source.parse([_NO_DATE_HTML])
    assert result[0]["date"] == ""


def test_parse_returns_empty_for_empty_input(source):
    result = source.parse([])
    assert result == []


def test_to_dict_sets_source_to_x(source):
    entry = {"url": "https://docs.x.com/changelog#x", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["source"] == "x"


def test_to_dict_sets_empty_summary(source):
    entry = {"url": "https://docs.x.com/changelog#x", "title": "X", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["summary"] == ""


def test_to_dict_preserves_url_and_title(source):
    entry = {"url": "https://docs.x.com/changelog#post", "title": "Post Title", "date": "2026-04-14"}
    result = source.to_dict(entry)
    assert result["url"] == "https://docs.x.com/changelog#post"
    assert result["title"] == "Post Title"


def test_run_filters_out_entry_missing_title(source, monkeypatch):
    monkeypatch.setattr(source, "fetch", lambda: [_NO_TITLE_HTML])
    result = source.run()
    assert result == []
