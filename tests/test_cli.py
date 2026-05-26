from unittest.mock import patch
from click.testing import CliRunner
from feedy.cli import cli


def _make_entries(source_name, count):
    return [
        {"url": f"https://{source_name}.com/{i}", "title": f"Title {i}", "date": "2026-05-27", "source": source_name, "summary": ""}
        for i in range(count)
    ]


@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_prints_per_source_summary(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage
):
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

    assert result.exit_code == 0
    assert "[telegram] 3 new, 0 skipped" in result.output
    assert "[tiktok] 1 new, 1 skipped" in result.output
    assert "[meta] 0 new, 0 skipped" in result.output
    assert "[hackernews] 4 new, 1 skipped" in result.output
    assert "Total: 8 new entries saved." in result.output


@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_total_counts_only_saved(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage
):
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


@patch("feedy.cli.storage")
@patch("feedy.cli.HackerNewsSource")
@patch("feedy.cli.MetaSource")
@patch("feedy.cli.TikTokSource")
@patch("feedy.cli.TelegramSource")
def test_fetch_continues_after_source_error(
    mock_telegram_cls, mock_tiktok_cls, mock_meta_cls, mock_hn_cls, mock_storage
):
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
