from feedy.config import DEFAULT_SOURCES, load_config


def test_load_config_returns_defaults_when_file_is_missing(tmp_path):
    config = load_config(tmp_path / "absent.toml")
    assert config.sources == DEFAULT_SOURCES


def test_load_config_defaults_output_format_to_markdown(tmp_path):
    assert load_config(tmp_path / "absent.toml").output_format == "markdown"
