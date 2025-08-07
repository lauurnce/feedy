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
