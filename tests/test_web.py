from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from feedy.web import app

client = TestClient(app)


def _entry(i, source="hackernews"):
    return {
        "id": i,
        "url": f"https://{source}.com/{i}",
        "title": f"Title {i}",
        "date": "2026-05-30",
        "source": source,
        "summary": "A summary.",
        "created_at": "2026-05-30 00:00:00",
    }


def test_root_returns_health():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"service": "feedy", "status": "ok"}


@patch("feedy.web.storage")
def test_digest_defaults_since_to_today(mock_storage):
    mock_storage.get_entries.return_value = []
    resp = client.get("/digest")
    today = datetime.now().strftime("%Y-%m-%d")
    mock_storage.get_entries.assert_called_once_with(source=None, since=today)
    assert resp.json()["since"] == today


@patch("feedy.web.storage")
def test_digest_returns_entries_and_count(mock_storage):
    entries = [_entry(1), _entry(2)]
    mock_storage.get_entries.return_value = entries
    resp = client.get("/digest")
    body = resp.json()
    assert body["count"] == 2
    assert body["entries"] == entries


@patch("feedy.web.storage")
def test_digest_passes_since_param(mock_storage):
    mock_storage.get_entries.return_value = []
    client.get("/digest?since=2026-05-01")
    mock_storage.get_entries.assert_called_once_with(source=None, since="2026-05-01")


@patch("feedy.web.storage")
def test_digest_passes_source_param(mock_storage):
    mock_storage.get_entries.return_value = []
    client.get("/digest?source=hackernews&since=2026-05-01")
    mock_storage.get_entries.assert_called_once_with(source="hackernews", since="2026-05-01")
