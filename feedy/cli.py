import click


@click.group()
def cli():
    """feedy — developer blog feed aggregator."""


@cli.command()
def fetch():
    """Fetch latest entries from all configured sources."""
    click.echo("fetch: not yet implemented")


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
