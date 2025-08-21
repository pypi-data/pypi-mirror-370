import click
from csv import DictWriter
from tabulate import tabulate
from making_with_code_cli.settings import read_settings
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.styles import (
    info,
)
from making_with_code_cli.teach.setup import check_required_teacher_settings
from making_with_code_cli.teach.section.create import create_section
from making_with_code_cli.teach.section.edit import edit_section
from making_with_code_cli.teach.section.show import show_section

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("-o", "--outfile", help="Save results as csv")
def section(ctx, config, outfile):
    "Manage sections of students"
    if ctx.invoked_subcommand is None:
        settings = read_settings(config)
        if not check_required_teacher_settings(settings):
            return
        api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
        roster = api.get_roster(settings['mwc_accounts_token'])
        if roster['teacher_sections']:
            data = summarize_sections(roster['teacher_sections'])
            if outfile:
                with open(outfile, "w") as fh:
                    writer = DictWriter(fh, data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            else:
                click.echo(info(tabulate(data, headers="keys"), preformatted=True))
        else:
            click.echo(info("You have no sections."))

def summarize_sections(section_data):
    for section in section_data:
        section["students"] = len(section["student_tokens"])
        del section["student_tokens"]
    return section_data

section.add_command(create_section)
section.add_command(edit_section)
section.add_command(show_section)

