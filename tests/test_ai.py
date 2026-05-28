import os
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from feedy.ai import complete


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
    result = complete("say hello")
    assert result is None


def test_complete_empty_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
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
