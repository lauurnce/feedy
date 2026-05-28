import click
from datetime import datetime

import feedy.storage as storage
from feedy.sources.hackernews import HackerNewsSource
from feedy.sources.meta import MetaSource
from feedy.sources.telegram import TelegramSource
from feedy.sources.tiktok import TikTokSource


@click.group()
def cli():
    """feedy — developer blog feed aggregator."""


@cli.command()
def fetch():
    """Fetch latest entries from all configured sources."""
    sources = [
        TelegramSource(),
        TikTokSource(),
        MetaSource(),
        HackerNewsSource(),
    ]
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
def digest():
    """Generate and print today's AI digest."""
    click.echo("digest: not yet implemented")


if __name__ == "__main__":
    cli()
