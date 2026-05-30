import smtplib
from unittest.mock import MagicMock, patch

import httpx

from feedy.config import EmailConfig
from feedy.notify import send_email, send_to_slack

_URL = "https://hooks.slack.com/services/T00/B00/xxxx"


def _email_cfg(**overrides):
    base = dict(
        host="smtp.example.com",
        port=587,
        username="user@example.com",
        password="secret",
        sender="user@example.com",
        recipient="dest@example.com",
    )
    base.update(overrides)
    return EmailConfig(**base)


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


@patch("feedy.notify.smtplib")
def test_send_email_sends_message(mock_smtplib):
    server = mock_smtplib.SMTP.return_value.__enter__.return_value
    send_email("digest body", "feedy digest — 2026-05-30", _email_cfg())
    mock_smtplib.SMTP.assert_called_once_with("smtp.example.com", 587, timeout=10)
    server.send_message.assert_called_once()


@patch("feedy.notify.smtplib")
def test_send_email_logs_in_with_credentials(mock_smtplib):
    server = mock_smtplib.SMTP.return_value.__enter__.return_value
    send_email("body", "subj", _email_cfg(username="u", password="p"))
    server.login.assert_called_once_with("u", "p")


@patch("feedy.notify.smtplib")
def test_send_email_skips_login_without_credentials(mock_smtplib):
    server = mock_smtplib.SMTP.return_value.__enter__.return_value
    send_email("body", "subj", _email_cfg(username=None, password=None))
    server.login.assert_not_called()


@patch("feedy.notify.smtplib")
def test_send_email_returns_true_on_success(mock_smtplib):
    assert send_email("body", "subj", _email_cfg()) is True


@patch("feedy.notify.smtplib")
def test_send_email_returns_false_on_smtp_error(mock_smtplib):
    mock_smtplib.SMTPException = smtplib.SMTPException
    mock_smtplib.SMTP.side_effect = smtplib.SMTPException("nope")
    assert send_email("body", "subj", _email_cfg()) is False
