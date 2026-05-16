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
