from datetime import datetime
from unittest.mock import patch
from click.testing import CliRunner
from feedy.cli import cli
from feedy.config import Config


def _make_entries(source_name, count):
    return [
        {"url": f"https://{source_name}.com/{i}", "title": f"Title {i}", "date": "2026-05-27", "source": source_name, "summary": ""}
        for i in range(count)
    ]


@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_prints_per_source_summary(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "tiktok", "meta", "hackernews"])
    mock_telegram_cls.return_value.name = "telegram"
    mock_telegram_cls.return_value.run.return_value = _make_entries("telegram", 3)
    mock_tiktok_cls.return_value.name = "tiktok"
    mock_tiktok_cls.return_value.run.return_value = _make_entries("tiktok", 2)
    mock_meta_cls.return_value.name = "meta"
    mock_meta_cls.return_value.run.return_value = _make_entries("meta", 0)
    mock_hn_cls.return_value.name = "hackernews"
    mock_hn_cls.return_value.run.return_value = _make_entries("hackernews", 5)

    mock_storage.save_many.side_effect = [
        (3, 0),  # telegram
        (1, 1),  # tiktok — 1 skipped (duplicate)
        (0, 0),  # meta
        (4, 1),  # hackernews
    ]

    runner = CliRunner()
    result = runner.invoke(cli, ["fetch"])

    # Assert run() called exactly once per source
    mock_telegram_cls.return_value.run.assert_called_once()
    mock_tiktok_cls.return_value.run.assert_called_once()
    mock_meta_cls.return_value.run.assert_called_once()
    mock_hn_cls.return_value.run.assert_called_once()

    # Assert save_many called 4 times (once per source)
    assert mock_storage.save_many.call_count == 4

    assert result.exit_code == 0
    assert "[telegram] 3 new, 0 skipped" in result.output
    assert "[tiktok] 1 new, 1 skipped" in result.output
    assert "[meta] 0 new, 0 skipped" in result.output
    assert "[hackernews] 4 new, 1 skipped" in result.output
    assert "Total: 8 new entries saved." in result.output


@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_total_counts_only_saved(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "tiktok", "meta", "hackernews"])
    for cls, name in [
        (mock_telegram_cls, "telegram"),
        (mock_tiktok_cls, "tiktok"),
        (mock_meta_cls, "meta"),
        (mock_hn_cls, "hackernews"),
    ]:
        cls.return_value.name = name
        cls.return_value.run.return_value = []

    mock_storage.save_many.side_effect = [(2, 0), (0, 3), (1, 0), (0, 0)]

    runner = CliRunner()
    result = runner.invoke(cli, ["fetch"])

    assert result.exit_code == 0
    assert "Total: 3 new entries saved." in result.output


@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_continues_after_source_error(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "tiktok", "meta", "hackernews"])
    mock_telegram_cls.return_value.name = "telegram"
    mock_telegram_cls.return_value.run.side_effect = RuntimeError("network down")

    mock_tiktok_cls.return_value.name = "tiktok"
    mock_tiktok_cls.return_value.run.return_value = []
    mock_meta_cls.return_value.name = "meta"
    mock_meta_cls.return_value.run.return_value = []
    mock_hn_cls.return_value.name = "hackernews"
    mock_hn_cls.return_value.run.return_value = []

    mock_storage.save_many.return_value = (0, 0)

    runner = CliRunner()
    result = runner.invoke(cli, ["fetch"])

    assert result.exit_code == 0
    assert "[telegram] error: network down" in result.output
    assert "[tiktok] 0 new, 0 skipped" in result.output
    assert "[meta] 0 new, 0 skipped" in result.output
    assert "[hackernews] 0 new, 0 skipped" in result.output


@patch("feedy.cli.load_config")
@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_only_runs_configured_sources(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage, mock_load_config
):
    mock_load_config.return_value = Config(sources=["telegram", "hackernews"])
    mock_telegram_cls.return_value.name = "telegram"
    mock_telegram_cls.return_value.run.return_value = []
    mock_hn_cls.return_value.name = "hackernews"
    mock_hn_cls.return_value.run.return_value = []
    mock_storage.save_many.return_value = (0, 0)

    runner = CliRunner()
    result = runner.invoke(cli, ["fetch"])

    mock_telegram_cls.return_value.run.assert_called_once()
    mock_hn_cls.return_value.run.assert_called_once()
    mock_tiktok_cls.return_value.run.assert_not_called()
    mock_meta_cls.return_value.run.assert_not_called()
    assert result.exit_code == 0
    assert "[telegram]" in result.output
    assert "[hackernews]" in result.output


def _make_list_entry(id_, source, date, title, url):
    return {"id": id_, "source": source, "date": date, "title": title, "url": url, "summary": ""}


@patch("feedy.cli.storage")
def test_list_prints_table_header(mock_storage):
    mock_storage.get_entries.return_value = [
        _make_list_entry(1, "hackernews", "2026-05-27", "Test Entry", "https://hn.com/1")
    ]
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "ID" in result.output
    assert "SOURCE" in result.output
    assert "DATE" in result.output
    assert "TITLE" in result.output
    assert "URL" in result.output


@patch("feedy.cli.storage")
def test_list_shows_entries(mock_storage):
    mock_storage.get_entries.return_value = [
        _make_list_entry(1, "hackernews", "2026-05-27", "Entry One", "https://hn.com/1"),
        _make_list_entry(2, "telegram", "2026-05-26", "Entry Two", "https://t.me/2"),
    ]
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Entry One" in result.output
    assert "Entry Two" in result.output
    assert "hackernews" in result.output
    assert "telegram" in result.output


@patch("feedy.cli.storage")
def test_list_no_entries(mock_storage):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No entries found." in result.output


@patch("feedy.cli.storage")
def test_list_filter_by_source(mock_storage):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["list", "--source", "hackernews"])
    mock_storage.get_entries.assert_called_once_with(source="hackernews", since=None)


@patch("feedy.cli.storage")
def test_list_filter_by_since(mock_storage):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["list", "--since", "2026-05-01"])
    mock_storage.get_entries.assert_called_once_with(source=None, since="2026-05-01")


@patch("feedy.cli.storage")
def test_list_invalid_since(mock_storage):
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--since", "bad-date"])
    assert result.exit_code != 0
    assert "YYYY-MM-DD" in result.output


@patch("feedy.cli.storage")
def test_list_truncates_long_title(mock_storage):
    long_title = "A" * 60
    mock_storage.get_entries.return_value = [
        _make_list_entry(1, "x", "2026-05-27", long_title, "https://x.com/1")
    ]
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert "A" * 45 in result.output
    assert "A" * 60 not in result.output


def _make_digest_entries(source_name, count):
    return [
        {"url": f"https://{source_name}.com/{i}", "title": f"Title {i}", "date": "2026-05-29", "source": source_name, "summary": ""}
        for i in range(count)
    ]


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_no_entries_prints_message(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    result = runner.invoke(cli, ["digest"])
    assert result.exit_code == 0
    assert "No entries found." in result.output
    mock_summarize.assert_not_called()
    mock_build_digest.assert_not_called()


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_calls_summarize_with_entries(mock_storage, mock_summarize, mock_build_digest):
    entries = _make_digest_entries("hackernews", 2)
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = entries
    mock_build_digest.return_value = ""
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_summarize.assert_called_once_with(entries)


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_calls_build_digest_with_summarized(mock_storage, mock_summarize, mock_build_digest):
    entries = _make_digest_entries("hackernews", 1)
    summarized = [{**entries[0], "summary": "A great summary."}]
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = summarized
    mock_build_digest.return_value = "## Hackernews\n• Title 0 — A great summary."
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_build_digest.assert_called_once_with(summarized)


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_prints_build_digest_output(mock_storage, mock_summarize, mock_build_digest):
    entries = _make_digest_entries("hackernews", 1)
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = entries
    mock_build_digest.return_value = "## Hackernews\n• Title 0"
    runner = CliRunner()
    result = runner.invoke(cli, ["digest"])
    assert result.exit_code == 0
    assert "## Hackernews" in result.output
    assert "Title 0" in result.output


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_defaults_since_to_today(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    today = datetime.now().strftime("%Y-%m-%d")
    mock_storage.get_entries.assert_called_once_with(source=None, since=today)


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_since_option_passed_to_storage(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["digest", "--since", "2026-05-01"])
    mock_storage.get_entries.assert_called_once_with(source=None, since="2026-05-01")


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_source_option_passed_to_storage(mock_storage, mock_summarize, mock_build_digest):
    mock_storage.get_entries.return_value = []
    runner = CliRunner()
    runner.invoke(cli, ["digest", "--source", "hackernews"])
    kwargs = mock_storage.get_entries.call_args[1]
    assert kwargs["source"] == "hackernews"


@patch("feedy.cli.build_digest")
@patch("feedy.cli.summarize")
@patch("feedy.cli.storage")
def test_digest_persists_new_summaries(mock_storage, mock_summarize, mock_build_digest):
    entries = [
        {"url": "https://hn.com/1", "title": "Post A", "date": "2026-05-29", "source": "hackernews", "summary": ""},
        {"url": "https://hn.com/2", "title": "Post B", "date": "2026-05-29", "source": "hackernews", "summary": "Already summarized."},
    ]
    summarized = [
        {"url": "https://hn.com/1", "title": "Post A", "date": "2026-05-29", "source": "hackernews", "summary": "New AI summary."},
        {"url": "https://hn.com/2", "title": "Post B", "date": "2026-05-29", "source": "hackernews", "summary": "Already summarized."},
    ]
    mock_storage.get_entries.return_value = entries
    mock_summarize.return_value = summarized
    mock_build_digest.return_value = ""
    runner = CliRunner()
    runner.invoke(cli, ["digest"])
    mock_storage.update_summary.assert_called_once_with("https://hn.com/1", "New AI summary.")
