from unittest.mock import MagicMock, patch

import httpx

from feedy.notify import send_to_slack

_URL = "https://hooks.slack.com/services/T00/B00/xxxx"


@patch("feedy.notify.httpx")
def test_send_to_slack_posts_text(mock_httpx):
    send_to_slack("hello digest", _URL)
    mock_httpx.post.assert_called_once()
    args, kwargs = mock_httpx.post.call_args
    assert args[0] == _URL
    assert kwargs["json"] == {"text": "hello digest"}


@patch("feedy.notify.httpx")
def test_send_to_slack_returns_true_on_success(mock_httpx):
    mock_httpx.post.return_value = MagicMock()
    assert send_to_slack("hi", _URL) is True


@patch("feedy.notify.httpx")
def test_send_to_slack_returns_false_on_http_error(mock_httpx):
    mock_httpx.HTTPError = httpx.HTTPError
    mock_httpx.post.side_effect = httpx.HTTPError("boom")
    assert send_to_slack("hi", _URL) is False
