# teach/setup.py
# --------------
# Implements `mwc teach setup`

import click
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.setup.tasks import (
    choose_mwc_username,
    prompt_mwc_password,
    choose_work_dir,
    choose_editor,
)
from making_with_code_cli.settings import (
    get_settings_path,
    read_settings, 
    write_settings,
)
from making_with_code_cli.styles import (
    address,
    question,
    info,
    debug as debug_fmt,
    confirm,
    error,
)

INTRO_MESSAGE = (
    "Welcome to Making with Code setup. "
    "This command will configure your teacher role. "
    "If you also have a student role, the same config file will be used "
    "by default. You can specify a separate config file using --config."
)

REQUIRED_TEACHER_SETTINGS = [
    'mwc_username',
    'mwc_accounts_token',
    'teacher_work_dir',
]

def check_required_teacher_settings(settings):
    missing_settings = [s for s in REQUIRED_TEACHER_SETTINGS if s not in settings]
    if missing_settings:
        click.echo(error("Some settings are missing. Please run mwc teach setup."))
    return not missing_settings
    
@click.command
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("--debug", is_flag=True, help="Show debug-level output")
@click.option("--git-name", help="Set git name")
@click.option("--git-email", help="Set git email address")
@click.option("--mwc-accounts-url", help="Set URL for MWC accounts server")
def setup(config, debug, git_name, git_email, mwc_accounts_url):
    """Configure teacher settings"""
    settings = read_settings(config)
    if debug:
        sp = get_settings_path(config)
        click.echo(debug_fmt(f"Reading settings from {sp}"))
    click.echo(address(INTRO_MESSAGE))
    click.echo()
    if git_name:
        settings['git_name'] = git_name
    if git_email:
        settings['git_email'] = git_email
    if mwc_accounts_url:
        settings['mwc_accounts_url'] = mwc_accounts_url
    settings['mwc_username'] = choose_mwc_username(settings.get("mwc_username"))
    api = MWCAccountsAPI(settings.get('mwc_accounts_url'))
    if not 'mwc_accounts_token' in settings:
        token = prompt_mwc_password(settings['mwc_username'], api)
        settings['mwc_accounts_token'] = token
    while True:
        try:
            status = api.get_status(settings['mwc_accounts_token'])
            break
        except api.RequestFailed as bad_token:
            if debug:
                click.echo(debug_fmt(bad_token))
            token = prompt_mwc_password(settings['mwc_username'], api)
            settings['mwc_accounts_token'] = token
    settings['mwc_git_token'] = status['git_token']
    settings['work_dir'] = str(choose_work_dir(settings.get("work_dir")).resolve())
    settings['editor'] = choose_editor(settings.get('editor', 'code'))
    settings['teacher_work_dir'] = str(choose_work_dir(
        settings.get("teacher_work_dir"), 
        teacher=True
    ))
    if debug:
        if settings.get('mwc_accounts_url'):
            click.echo(debug_fmt(f"Using custom MWC accounts server: {settings['mwc_accounts_url']}"))
        click.echo(debug_fmt("MWC Accounts Server status:"))
        click.echo(debug_fmt(str(status)))
    write_settings(settings, config)

