import click
from csv import DictWriter
from making_with_code_cli.settings import read_settings
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.styles import (
    address, 
    error,
    info,
    question,
)

@click.command('show')
@click.argument("slug")
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("-o", "--outfile", help="Save results as csv")
def show_section(config, slug, outfile):
    "Show section details"
    settings = read_settings(config)
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    params = {"slug": slug}
    response = api.get_roster(settings.get('mwc_accounts_token'))
    try:
        section = get_section(response, slug)
    except ValueError as err:
        click.echo(error(str(err)))
    if outfile:
        students = section['student_tokens']
        result = [{"username": s, "git_token": t, "section": slug} for s, t in students.items()]
        if not result:
            click.echo(error(f"Nothing to write; there are no students in {slug}."))
            return
        with open(outfile, "w") as fh:
            writer = DictWriter(fh, result[0].keys())
            writer.writeheader()
            writer.writerows(result)
    else:
        click.echo(info(f"name: {section['name']}"))
        click.echo(info(f"slug: {section['slug']}"))
        click.echo(info(f"course: {section['course_name']}"))
        click.echo(info(f"curriculum site: {section['curriculum_site_url']}"))
        click.echo(info(f"join code: {section['code']}"))
        if section['student_tokens']:
            click.echo(info("students:"))
            for student in sorted(section['student_tokens'].keys()):
                click.echo(info(f" - {student}"))
        else:
            click.echo(info("students: []"))

def get_section(roster, slug):
    for section in roster['teacher_sections']:
        if section['slug'] == slug:
            return section
    raise ValueError(f"Invalid section {slug}")
