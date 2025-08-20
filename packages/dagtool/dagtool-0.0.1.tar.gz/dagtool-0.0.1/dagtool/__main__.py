import click

from .__about__ import __version__


@click.group()
def cli() -> None:
    """Main Tool CLI."""


@cli.command("version")
def version() -> None:
    click.echo(__version__)


if __name__ == "__main__":
    cli()
