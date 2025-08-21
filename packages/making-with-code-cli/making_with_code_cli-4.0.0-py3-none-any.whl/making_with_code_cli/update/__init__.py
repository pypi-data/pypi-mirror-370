import click
import traceback
from pathlib import Path
from making_with_code_cli.settings import read_settings
from making_with_code_cli.curriculum import get_curriculum
from making_with_code_cli.git_backend import get_backend
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.setup.tasks import WORK_DIR_PERMISSIONS
from making_with_code_cli.styles import (
    address,
    question,
    info,
    debug as debug_fmt,
    confirm,
    error,
)

@click.command()
@click.option("--config", help="Path to config file (default: ~/.mwc)")
def update(config):
    """Update the MWC work directory"""
    settings = read_settings(config)
    if not settings:
        click.echo(error(f"Please run mwc setup first."))
        return
    mwc_home = Path(settings["work_dir"])
    if not mwc_home.exists():
        mwc_home.mkdir(mode=WORK_DIR_PERMISSIONS, parents=True)
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    try:
        status = api.get_status(settings.get('mwc_accounts_token'))
    except api.RequestFailed as bad_token:
        click.echo(error(f"Error logging into MWC accounts server. Please run mwc setup."))
        return
    for course in status['student_section_memberships']:
        curr = get_curriculum(course['curriculum_site_url'], course['course_name'])
        git_backend = get_backend(curr['git_backend'])(settings)
        course_dir = mwc_home / curr['slug']
        course_dir.mkdir(mode=WORK_DIR_PERMISSIONS, exist_ok=True)
        for unit in curr['units']:
            unit_dir = course_dir / unit['slug']
            unit_dir.mkdir(mode=WORK_DIR_PERMISSIONS, exist_ok=True)
            for module in unit['modules']:
                module_dir = unit_dir / module['slug']
                if module_dir.exists():
                    try:
                        git_backend.update(module, module_dir)
                    except Exception as e:
                        msg =  traceback.format_exception(type(e), e, e.__traceback__)
                        click.echo(error(''.join(msg), preformatted=True))
                else:
                    rel_dir = module_dir.resolve().relative_to(mwc_home)
                    click.echo(confirm(f"Initializing {module['slug']} at {rel_dir}."))
                    click.echo(info(f"See {module['url']} for details."))
                    try:
                        git_backend.init_module(module, module_dir)
                    except Exception as e:
                        msg =  traceback.format_exception(type(e), e, e.__traceback__)
                        click.echo(error(''.join(msg), preformatted=True))
