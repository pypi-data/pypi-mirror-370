import click
from importlib.metadata import metadata
from making_with_code_cli.styles import (
    address,
)

@click.command()
def version():
    "Print MWC version"
    version = metadata('making-with-code-cli')['version']
    click.echo(address("MWC " + version, preformatted=True))
