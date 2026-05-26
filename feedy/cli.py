import click

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
def list_entries():
    """List saved entries from the database."""
    click.echo("list: not yet implemented")


@cli.command()
def digest():
    """Generate and print today's AI digest."""
    click.echo("digest: not yet implemented")


if __name__ == "__main__":
    cli()
