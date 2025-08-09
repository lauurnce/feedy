from feedy.config import DEFAULT_SOURCES, load_config


def test_load_config_returns_defaults_when_file_is_missing(tmp_path):
    config = load_config(tmp_path / "absent.toml")
    assert config.sources == DEFAULT_SOURCES
