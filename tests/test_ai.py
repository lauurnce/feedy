import os
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from feedy.ai import complete
from feedy.config import Config


def _mock_client(text: str) -> MagicMock:
    """Build a mock anthropic.Anthropic that returns `text` from messages.create."""
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    client = MagicMock()
    client.messages.create.return_value = msg
    return client


def test_complete_returns_text(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = _mock_client("  hello world  ")
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result == "hello world"


def test_complete_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("feedy.ai.load_config", return_value=Config(api_key=None)):
        result = complete("say hello")
    assert result is None


def test_complete_empty_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    with patch("feedy.ai.load_config", return_value=Config(api_key=None)):
        result = complete("say hello")
    assert result is None


def test_complete_api_error(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.APIError(
        message="rate limited", request=MagicMock(), body=None
    )
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result is None


def test_complete_empty_content(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    msg = MagicMock()
    msg.content = []
    mock_client = MagicMock()
    mock_client.messages.create.return_value = msg
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result is None


def test_complete_falls_back_to_config_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    mock_client = _mock_client("from config")
    with patch("feedy.ai.load_config", return_value=Config(api_key="cfg-key")), \
         patch("feedy.ai.anthropic.Anthropic", return_value=mock_client) as mock_anthropic:
        result = complete("say hello")
    assert result == "from config"
    mock_anthropic.assert_called_once_with(api_key="cfg-key")


def test_complete_env_key_takes_precedence_over_config(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    mock_client = _mock_client("from env")
    with patch("feedy.ai.load_config", return_value=Config(api_key="cfg-key")), \
         patch("feedy.ai.anthropic.Anthropic", return_value=mock_client) as mock_anthropic:
        result = complete("say hello")
    assert result == "from env"
    mock_anthropic.assert_called_once_with(api_key="env-key")


def test_complete_non_text_content(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    msg = MagicMock()
    non_text_block = MagicMock(spec=[])  # no .text attribute
    msg.content = [non_text_block]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = msg
    with patch("feedy.ai.anthropic.Anthropic", return_value=mock_client):
        result = complete("say hello")
    assert result is None
