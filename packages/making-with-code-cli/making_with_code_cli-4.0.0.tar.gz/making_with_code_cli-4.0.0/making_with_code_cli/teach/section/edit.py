import click
from tabulate import tabulate
from making_with_code_cli.settings import read_settings
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.curriculum import get_curriculum
from making_with_code_cli.errors import CurriculumSiteNotAvailable, MWCError
from making_with_code_cli.styles import (
    address, 
    error,
    info,
    question,
)

@click.command('edit')
@click.argument("slug")
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("--name", help="Section name")
@click.option("--curriculum-site-url", help="URL for curriculum website. e.g. https://makingwithcode.org")
@click.option("--course-name", help="MWC course name")
@click.option("--code", help="Code students can use to join the section")
@click.option("--roster", help="csv file containing student information")
def edit_section(config, slug, name, curriculum_site_url, course_name, code, roster):
    "Edit an existing section"
    settings = read_settings(config)
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    params = {"slug": slug}
    if name: 
        params["name"] = name
    if curriculum_site_url:
        params["curriculum_site_url"] = curriculum_site_url
    if course_name:
        params["course_name"] = course_name
    if code: 
        params["code"] = code
    try:
        response = api.update_section(settings.get('mwc_accounts_token'), params)
        click.echo(info(tabulate([response], headers="keys"), preformatted=True))
    except api.RequestFailed as err:
        click.echo(error(f"Could not edit section {params['slug']}:"))
        for field, problems in err.data.items():
            click.echo(error(f" - {field}: {'; '.join(problems)}"))
