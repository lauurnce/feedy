from feedy.digest import build_digest


def test_single_entry_with_summary():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Great summary here."}]
    result = build_digest(entries)
    assert "• My Post — Great summary here." in result


def test_single_entry_without_summary():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": ""}]
    result = build_digest(entries)
    assert "• My Post" in result
    assert " — " not in result


def test_multiple_sources_sorted_alphabetically():
    entries = [
        {"url": "https://ex.com/1", "title": "Post 1", "date": "2026-05-29", "source": "telegram", "summary": "Sum 1."},
        {"url": "https://ex.com/2", "title": "Post 2", "date": "2026-05-29", "source": "hackernews", "summary": "Sum 2."},
    ]
    result = build_digest(entries)
    assert "## Hackernews" in result
    assert "## Telegram" in result
    assert result.index("## Hackernews") < result.index("## Telegram")


def test_empty_input_returns_empty_string():
    assert build_digest([]) == ""


def test_source_header_capitalized():
    entries = [{"url": "https://ex.com", "title": "Post", "date": "2026-05-29", "source": "hackernews", "summary": "Sum."}]
    result = build_digest(entries)
    assert "## Hackernews" in result


def test_groups_separated_by_blank_line():
    entries = [
        {"url": "https://ex.com/1", "title": "Post 1", "date": "2026-05-29", "source": "telegram", "summary": "Sum 1."},
        {"url": "https://ex.com/2", "title": "Post 2", "date": "2026-05-29", "source": "meta", "summary": "Sum 2."},
    ]
    result = build_digest(entries)
    sections = result.split("\n\n")
    assert len(sections) == 2


def test_plain_format_has_no_markdown_header():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Sum."}]
    result = build_digest(entries, output_format="plain")
    assert "## " not in result
    assert "TELEGRAM" in result


def test_plain_format_uses_dash_bullet():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Sum."}]
    result = build_digest(entries, output_format="plain")
    assert "- My Post — Sum." in result
    assert "•" not in result


def test_markdown_is_default():
    entries = [{"url": "https://ex.com", "title": "My Post", "date": "2026-05-29", "source": "telegram", "summary": "Sum."}]
    result = build_digest(entries)
    assert "## Telegram" in result
    assert "• My Post — Sum." in result
