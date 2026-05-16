import pytest
import feedy.storage as storage


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")


def test_save_works_without_calling_init_db():
    # Must not require explicit init_db() call first
    result = storage.save({"url": "https://a.com", "title": "A", "date": "2026-05-17", "source": "x", "summary": ""})
    assert result is True
