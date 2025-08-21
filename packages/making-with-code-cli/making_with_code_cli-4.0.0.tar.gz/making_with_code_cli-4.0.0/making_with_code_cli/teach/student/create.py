import click
from tabulate import tabulate
from making_with_code_cli.settings import read_settings
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.styles import (
    info,
    error,
)

@click.command("create")
@click.argument("username")
@click.argument("password")
@click.argument("section")
@click.option("--config", help="Path to config file (default: ~/.mwc)")
def create_student(username, password, section, config):
    "Create a student user"
    settings = read_settings(config)
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    params = {
        "username": username, 
        "password": password, 
        "section": section,
    }
    try:
        response = api.create_student(settings.get('mwc_accounts_token'), params)
        click.echo(info(f"Created student {response['username']} in {section}."))
    except api.RequestFailed as err:
        click.echo(error(f"Could not create {params['username']}:"))
        print(err)
        for field, problems in err.data.items():
            click.echo(error(f" - {field}: {'; '.join(problems)}"))


