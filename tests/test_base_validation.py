from feedy.sources.base import BaseFeedSource


def _entry(url="https://a.com", title="A"):
    return {"url": url, "title": title, "date": "", "source": "x", "summary": ""}


def test_is_valid_accepts_entry_with_url_and_title():
    assert BaseFeedSource._is_valid(_entry()) is True
