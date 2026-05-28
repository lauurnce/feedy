import pytest
import feedy.storage as storage


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")


def test_save_works_without_calling_init_db():
    # Must not require explicit init_db() call first
    result = storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-17", "source": "x", "summary": ""})
    assert result is True


def test_save_returns_true_on_new_entry():
    result = storage.save({"url": "https://b.com", "title": "B", "date": "2026-05-17", "source": "x", "summary": ""})
    assert result is True


def test_save_returns_false_on_duplicate_url():
    entry = {"url": "https://c.com", "title": "C", "date": "2026-05-17", "source": "x", "summary": ""}
    storage.save(entry)
    result = storage.save(entry)
    assert result is False


def test_save_stores_entry_retrievable_via_all_entries():
    storage.save({"url": "https://d.com", "title": "D", "date": "2026-05-17", "source": "x", "summary": ""})
    entries = storage.all_entries()
    assert len(entries) == 1
    assert entries[0]["url"] == "https://d.com"
    assert entries[0]["title"] == "D"


def test_save_many_returns_saved_and_skipped_counts():
    entries = [
        {"url": "https://e.com", "title": "E", "date": "2026-05-17", "source": "x", "summary": ""},
        {"url": "https://f.com", "title": "F", "date": "2026-05-17", "source": "x", "summary": ""},
    ]
    saved, skipped = storage.save_many(entries)
    assert saved == 2
    assert skipped == 0


def test_save_many_counts_duplicates_as_skipped():
    entry = {"url": "https://g.com", "title": "G", "date": "2026-05-17", "source": "x", "summary": ""}
    storage.save(entry)  # pre-insert duplicate
    entries = [
        entry,  # duplicate
        {"url": "https://h.com", "title": "H", "date": "2026-05-17", "source": "x", "summary": ""},
    ]
    saved, skipped = storage.save_many(entries)
    assert saved == 1
    assert skipped == 1


def test_save_many_empty_list_returns_zero_zero():
    saved, skipped = storage.save_many([])
    assert saved == 0
    assert skipped == 0


def test_update_summary_returns_true_when_url_exists():
    storage.save({"url": "https://i.com", "title": "I", "date": "2026-05-17", "source": "x", "summary": ""})
    result = storage.update_summary("https://i.com", "AI wrote this.")
    assert result is True


def test_update_summary_persists_new_summary():
    storage.save({"url": "https://j.com", "title": "J", "date": "2026-05-17", "source": "x", "summary": ""})
    storage.update_summary("https://j.com", "Updated summary.")
    entries = storage.all_entries()
    match = next(e for e in entries if e["url"] == "https://j.com")
    assert match["summary"] == "Updated summary."


def test_update_summary_returns_false_when_url_missing():
    result = storage.update_summary("https://notexist.com", "ghost")
    assert result is False


def test_get_entries_empty_db():
    entries = storage.get_entries()
    assert entries == []


def test_get_entries_no_filter():
    storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-27", "source": "hackernews", "summary": ""})
    storage.save({"url": "https://b.com", "title": "B", "date": "2026-05-26", "source": "telegram", "summary": ""})
    entries = storage.get_entries()
    assert len(entries) == 2


def test_get_entries_filter_source():
    storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-27", "source": "hackernews", "summary": ""})
    storage.save({"url": "https://b.com", "title": "B", "date": "2026-05-26", "source": "telegram", "summary": ""})
    entries = storage.get_entries(source="hackernews")
    assert len(entries) == 1
    assert entries[0]["source"] == "hackernews"


def test_get_entries_filter_since():
    storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-25", "source": "x", "summary": ""})
    storage.save({"url": "https://b.com", "title": "B", "date": "2026-05-27", "source": "x", "summary": ""})
    entries = storage.get_entries(since="2026-05-26")
    assert len(entries) == 1
    assert entries[0]["url"] == "https://b.com"


def test_get_entries_both_filters():
    storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-27", "source": "hackernews", "summary": ""})
    storage.save({"url": "https://b.com", "title": "B", "date": "2026-05-27", "source": "telegram", "summary": ""})
    storage.save({"url": "https://c.com", "title": "C", "date": "2026-05-25", "source": "hackernews", "summary": ""})
    entries = storage.get_entries(source="hackernews", since="2026-05-26")
    assert len(entries) == 1
    assert entries[0]["url"] == "https://a.com"
