import click
from tabulate import tabulate
from making_with_code_cli.settings import read_settings
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.styles import (
    info,
    error,
)

@click.command("update")
@click.argument("username")
@click.argument("password")
@click.option("--config", help="Path to config file (default: ~/.mwc)")
def update_student(username, password, config):
    "Update a student's password"
    settings = read_settings(config)
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    params = {
        "username": username, 
        "password": password, 
    }
    try:
        response = api.update_student(settings.get('mwc_accounts_token'), params)
        click.echo(info(f"Updated student {response['username']}."))
    except api.RequestFailed as err:
        click.echo(error(f"Could not update {params['username']}:"))
        for field, problems in err.data.items():
            click.echo(error(f" - {field}: {'; '.join(problems)}"))

