from pathlib import Path

from feedy.config import Config, EmailConfig, load_config


def test_missing_file_returns_defaults(tmp_path):
    cfg = load_config(tmp_path / "nope.toml")
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic", "x"]
    assert cfg.output_format == "markdown"
    assert cfg.api_key is None


def test_default_config_constructor():
    cfg = Config()
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic", "x"]
    assert cfg.output_format == "markdown"
    assert cfg.api_key is None


def test_reads_sources(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('sources = ["telegram", "hackernews"]\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.sources == ["telegram", "hackernews"]


def test_reads_output_format(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('output_format = "plain"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.output_format == "plain"


def test_reads_api_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[anthropic]\napi_key = "sk-test-123"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.api_key == "sk-test-123"


def test_partial_file_uses_defaults_for_missing_keys(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('output_format = "plain"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.output_format == "plain"
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic", "x"]
    assert cfg.api_key is None


def test_empty_anthropic_table_gives_none_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[anthropic]\n", encoding="utf-8")
    cfg = load_config(path)
    assert cfg.api_key is None


def test_default_slack_webhook_is_none():
    cfg = Config()
    assert cfg.slack_webhook_url is None


def test_reads_slack_webhook(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[slack]\nwebhook_url = "https://hooks.slack.com/services/X"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.slack_webhook_url == "https://hooks.slack.com/services/X"


def test_default_email_is_none():
    cfg = Config()
    assert cfg.email is None


def test_reads_email_table(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(
        "[email]\n"
        'host = "smtp.gmail.com"\n'
        "port = 465\n"
        'username = "me@gmail.com"\n'
        'password = "app-pw"\n'
        'sender = "me@gmail.com"\n'
        'recipient = "you@gmail.com"\n',
        encoding="utf-8",
    )
    cfg = load_config(path)
    assert isinstance(cfg.email, EmailConfig)
    assert cfg.email.host == "smtp.gmail.com"
    assert cfg.email.port == 465
    assert cfg.email.username == "me@gmail.com"
    assert cfg.email.recipient == "you@gmail.com"


def test_email_table_defaults_port_587(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[email]\nhost = "smtp.example.com"\nrecipient = "you@example.com"\n', encoding="utf-8")
    cfg = load_config(path)
    assert cfg.email.port == 587
