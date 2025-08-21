import click
from making_with_code_cli.version import version
from making_with_code_cli.setup import setup
from making_with_code_cli.update import update
from making_with_code_cli.submit import submit
from making_with_code_cli.teach import teach

@click.group()
def cli():
    "Command line interface for Making with Code"

cli.add_command(version)
cli.add_command(setup)
cli.add_command(update)
cli.add_command(submit)
cli.add_command(teach)
