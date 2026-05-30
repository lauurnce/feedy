import os

import click
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import feedy.storage as storage
from feedy.config import load_config
from feedy.digest import build_digest
from feedy.notify import send_email, send_to_slack
from feedy.summarizer import summarize
from feedy.sources.anthropic import AnthropicSource
from feedy.sources.hackernews import HackerNewsSource
from feedy.sources.meta import MetaSource
from feedy.sources.openai import OpenAISource
from feedy.sources.telegram import TelegramSource
from feedy.sources.tiktok import TikTokSource


@click.group()
def cli():
    """feedy — developer blog feed aggregator."""


def _build_sources(names):
    registry = {
        "telegram": TelegramSource,
        "tiktok": TikTokSource,
        "meta": MetaSource,
        "hackernews": HackerNewsSource,
        "openai": OpenAISource,
        "anthropic": AnthropicSource,
    }
    return [registry[name]() for name in names if name in registry]


@cli.command()
def fetch():
    """Fetch latest entries from all configured sources."""
    config = load_config()
    sources = _build_sources(config.sources)
    total_saved = 0
    for source in sources:
        try:
            entries = source.run()
            saved, skipped = storage.save_many(entries)
            click.echo(f"[{source.name}] {saved} new, {skipped} skipped")
            total_saved += saved
        except Exception as e:
            click.echo(f"[{source.name}] error: {e}", err=True)

    click.echo("---")
    click.echo(f"Total: {total_saved} new entries saved.")


@cli.command("list")
@click.option("--source", default=None, help="Filter by source name.")
@click.option("--since", default=None, help="Filter entries on or after date (YYYY-MM-DD).")
def list_entries(source, since):
    """List saved entries from the database."""
    if since is not None:
        try:
            datetime.strptime(since, "%Y-%m-%d")
        except ValueError:
            raise click.BadParameter("use YYYY-MM-DD format", param_hint="'--since'")

    entries = storage.get_entries(source=source, since=since)

    if not entries:
        click.echo("No entries found.")
        return

    header = f"{'ID':<5} {'SOURCE':<13} {'DATE':<12} {'TITLE':<47} URL"
    click.echo(header)
    for e in entries:
        title = (e["title"] or "")[:45]
        row = f"{e['id']:<5} {(e['source'] or ''):<13} {(e['date'] or ''):<12} {title:<47} {e['url']}"
        click.echo(row)


@cli.command()
@click.option("--since", default=None, help="Filter entries on or after date (YYYY-MM-DD). Defaults to today.")
@click.option("--source", default=None, help="Filter by source name.")
@click.option("--output", "-o", default=None, type=click.Path(dir_okay=False, writable=True),
              help="Write the digest to a file instead of printing it.")
@click.option("--slack", is_flag=True, help="Send the digest to the configured Slack webhook.")
@click.option("--email", is_flag=True, help="Send the digest over SMTP to the configured recipient.")
def digest(since, source, output, slack, email):
    """Generate and print today's AI digest."""
    if since is None:
        since = datetime.now().strftime("%Y-%m-%d")

    entries = storage.get_entries(source=source, since=since)
    if not entries:
        click.echo("No entries found.")
        return

    config = load_config()
    summarized = summarize(entries)

    for original, updated in zip(entries, summarized):
        if updated["summary"] and updated["summary"] != original["summary"]:
            storage.update_summary(updated["url"], updated["summary"])

    text = build_digest(summarized, config.output_format)

    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
        click.echo(f"Digest written to {output}")
    elif not slack and not email:
        click.echo(text)

    if slack:
        webhook_url = os.environ.get("FEEDY_SLACK_WEBHOOK") or config.slack_webhook_url
        if not webhook_url:
            click.echo("No Slack webhook configured.", err=True)
        elif send_to_slack(text, webhook_url):
            click.echo("Digest sent to Slack.")
        else:
            click.echo("Failed to send digest to Slack.", err=True)

    if email:
        if config.email is None or not config.email.recipient:
            click.echo("No email configured.", err=True)
        else:
            password = os.environ.get("FEEDY_SMTP_PASSWORD") or config.email.password
            email_cfg = replace(config.email, password=password)
            subject = f"feedy digest — {since}"
            if send_email(text, subject, email_cfg):
                click.echo("Digest emailed.")
            else:
                click.echo("Failed to send email.", err=True)


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind the web server.")
@click.option("--port", default=8000, type=int, help="Port to bind the web server.")
def serve(host, port):
    """Serve today's digest as JSON over HTTP."""
    import uvicorn

    from feedy.web import app

    click.echo(f"Serving feedy API on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
