"""Digest delivery channels: Slack webhook and SMTP email."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

import httpx


def send_to_slack(text: str, webhook_url: str) -> bool:
    """POST the digest text to a Slack incoming webhook. Return True on success."""
    try:
        response = httpx.post(webhook_url, json={"text": text}, timeout=10)
        response.raise_for_status()
        return True
    except httpx.HTTPError as err:
        print(f"[slack] send failed: {err}")
        return False


def send_email(text: str, subject: str, cfg) -> bool:
    """Send the digest over SMTP using cfg (EmailConfig). Return True on success."""
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = cfg.sender
    message["To"] = cfg.recipient
    message.set_content(text)
    try:
        with smtplib.SMTP(cfg.host, cfg.port, timeout=10) as server:
            server.starttls()
            if cfg.username and cfg.password:
                server.login(cfg.username, cfg.password)
            server.send_message(message)
        return True
    except (smtplib.SMTPException, OSError) as err:
        print(f"[email] send failed: {err}")
        return False
