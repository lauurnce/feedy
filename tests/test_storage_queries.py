import pytest

import feedy.storage as storage


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")


def _entry(url, source="hackernews", date="2026-05-17"):
    return {"url": url, "title": url, "date": date, "source": source, "summary": ""}


def test_get_entries_returns_empty_list_on_fresh_database():
    assert storage.get_entries() == []


def test_get_entries_filters_by_source():
    storage.save(_entry("https://a.com", source="hackernews"))
    storage.save(_entry("https://b.com", source="openai"))
    rows = storage.get_entries(source="openai")
    assert [r["url"] for r in rows] == ["https://b.com"]


def test_get_entries_filters_by_since_date():
    storage.save(_entry("https://old.com", date="2026-01-01"))
    storage.save(_entry("https://new.com", date="2026-06-01"))
    rows = storage.get_entries(since="2026-05-01")
    assert [r["url"] for r in rows] == ["https://new.com"]


def test_get_entries_combines_source_and_since_with_and():
    storage.save(_entry("https://a.com", source="openai", date="2026-01-01"))
    storage.save(_entry("https://b.com", source="openai", date="2026-06-01"))
    storage.save(_entry("https://c.com", source="meta", date="2026-06-01"))
    rows = storage.get_entries(source="openai", since="2026-05-01")
    assert [r["url"] for r in rows] == ["https://b.com"]


def test_get_stats_returns_empty_mapping_on_fresh_database():
    assert storage.get_stats() == {}


def test_get_stats_counts_entries_per_source():
    storage.save(_entry("https://a.com", source="openai"))
    storage.save(_entry("https://b.com", source="openai"))
    storage.save(_entry("https://c.com", source="meta"))
    assert storage.get_stats() == {"meta": 1, "openai": 2}


def test_update_summary_returns_false_for_unknown_url():
    assert storage.update_summary("https://missing.com", "text") is False
