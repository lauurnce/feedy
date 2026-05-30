from pathlib import Path

from feedy.config import Config, load_config


def test_missing_file_returns_defaults(tmp_path):
    cfg = load_config(tmp_path / "nope.toml")
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic"]
    assert cfg.output_format == "markdown"
    assert cfg.api_key is None


def test_default_config_constructor():
    cfg = Config()
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic"]
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
    assert cfg.sources == ["telegram", "tiktok", "meta", "hackernews", "openai", "anthropic"]
    assert cfg.api_key is None


def test_empty_anthropic_table_gives_none_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[anthropic]\n", encoding="utf-8")
    cfg = load_config(path)
    assert cfg.api_key is None
