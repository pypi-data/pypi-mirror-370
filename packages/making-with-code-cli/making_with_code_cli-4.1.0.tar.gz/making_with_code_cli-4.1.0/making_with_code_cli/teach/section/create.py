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

MWC_CURRICULUM_URL = "https://makingwithcode.org"

@click.command('create')
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("--slug", help="Unique short identifier for the section")
@click.option("--name", help="Section name")
@click.option("--curriculum-site-url", help="URL for curriculum website. e.g. https://makingwithcode.org")
@click.option("--course-name", help="MWC course name")
@click.option("--code", help="Code students can use to join the section")
def create_section(config, slug, name, curriculum_site_url, course_name, code):
    "Create a new student section"
    settings = read_settings(config)
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    params = {
        "name": name, 
        "slug": slug, 
        "curriculum_site_url": curriculum_site_url,
        "course_name": course_name,
        "code": code,
    }
    if not params_complete(params):
        params = prompt_for_params(params)
    try:
        response = api.create_section(settings.get('mwc_accounts_token'), params)
        click.echo(info(tabulate([response], headers="keys"), preformatted=True))
    except api.RequestFailed as err:
        click.echo(error("Could not create new section:"))
        for field, problems in err.data.items():
            click.echo(error(f" - {field}: {'; '.join(problems)}"))

def params_complete(params):
    """Check whether all params are present.
    """
    required_params = ["name", "slug", "curriculum_site_url", "course_name", "code"]
    if all(params.get(p) for p in required_params):
        curriculum = get_curriculum(params["curriculum_site_url"])
        courses = [c["name"] for c in curriculum.get("courses", [])]
        if params["course_name"] in courses:
            return True
    return False

def prompt_for_params(params):
    """Interactively prompt user for missing params.
    """
    params['name'] = click.prompt(question("Section name"), default=params.get('name'))
    params['slug'] = click.prompt(question("Section slug"), default=params.get('slug'))
    while True:
        url = click.prompt(
            question("Curriculum site URL"), 
            default=params.get('curriculum_site_url') or  MWC_CURRICULUM_URL
        )
        try:
            curriculum = get_curriculum(url)
            params['curriculum_site_url'] = url
            if not curriculum.get('courses'):
                raise MWCError("Found the curriculum site, but no courses are published.")
            break
        except CurriculumSiteNotAvailable as err:
            click.echo(error(err))
    course_names = [c['name'] for c in curriculum['courses']]
    if params.get('course_name') and params.get('course_name') not in course_names:
        click.echo(info(f"Course name {params['course_name']} is invalid."))
        del params['course_name']
    if not params.get('course_name'):
        click.echo(info(f"The following courses are published at {params['curriculum_site_url']}:"))
        for name in course_names:
            click.echo(info(f" - {name}"))
        params['course_name'] = click.prompt(
            question("Course name"), 
            type=click.Choice(course_names), 
            default=params.get('course_name')
        )
    params['code'] = click.prompt(question("Join code"), default=params.get("code"))
    return params

