import click
from subprocess import run
import traceback
import yaml
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.git_backend import get_backend
from making_with_code_cli.update import update
from making_with_code_cli.decorators import handle_mwc_errors
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
from making_with_code_cli.setup.tasks import (
    INTRO_MESSAGE,
    INTRO_NOTES,
    WORK_DIR_PERMISSIONS,
    Platform,
    choose_mwc_username,
    prompt_mwc_password,
    choose_work_dir,
    choose_course,
    choose_editor,
    InstallXCode,
    InstallPoetry,
    InstallGit,
    InstallTree,
    InstallVSCode,
    InstallImageMagick,
    InstallHttpie,
    InstallScipy,
    GitConfiguration,
)

@click.command()
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("--debug", is_flag=True, help="Show debug-level output")
@click.option("--git-name", help="Set git name")
@click.option("--git-email", help="Set git email address")
@click.option("--mwc-accounts-url", help="Set URL for MWC accounts server")
@click.pass_context
@handle_mwc_errors
def setup(ctx, config, debug, git_name, git_email, mwc_accounts_url):
    """Set up the MWC command line interface"""
    settings = read_settings(config)
    sp = get_settings_path(config)
    if debug:
        click.echo(debug_fmt(f"Reading settings from {sp}"))
    if not sp.parent.exists():
        if click.confirm(confirm(f"Directory {sp.parent} doesn't exist. Create it?")):
            sp.parent.mkdir(parents=True)
        else:
            click.error(f"Could not save config file at {sp}.")
            return
    rc_tasks = []
    click.echo(address(INTRO_MESSAGE))
    for note in INTRO_NOTES:
        click.echo(address(note, list_format=True))
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
            click.echo(error("Sorry, there was an error logging in."))
            if debug:
                click.echo(debug_fmt(bad_token))
            token = prompt_mwc_password(settings['mwc_username'], api)
            settings['mwc_accounts_token'] = token
    settings['mwc_git_token'] = status['git_token']
    settings['work_dir'] = str(choose_work_dir(settings.get("work_dir")).resolve())
    settings['editor'] = choose_editor(settings.get('editor', 'code'))
    if debug:
        if settings.get('mwc_accounts_url'):
            click.echo(debug_fmt(f"Using custom MWC accounts server: {settings['mwc_accounts_url']}"))
        click.echo(debug_fmt("MWC Accounts Server status:"))
        click.echo(debug_fmt(str(status)))
        click.echo(info("MWC settings:"))
        click.echo(info(yaml.dump(settings), preformatted=True))
    write_settings(settings, config)

    task_classes = [
        InstallXCode,
        InstallPoetry,
        InstallGit,
        InstallTree,
        InstallVSCode,
        InstallImageMagick,
        InstallHttpie,
        #InstallScipy,
        GitConfiguration,
    ]
    errors = []
    for task_class in task_classes:
        try:
            task = task_class(settings, debug=debug)
            task.run_task_if_needed()
        except Exception as e:
            errors.append(task)
            click.echo(error('-' * 80))
            click.echo(error(f"{task.description} failed"))
            if debug:
                click.echo(debug_fmt(traceback.format_exc(), preformatted=True))
    if errors:
        click.echo(error(f"{len(errors)} setup tasks failed:"))
        for task in errors:
            click.echo(error(f"- {task.description}"))
    else:
        ctx.invoke(update, config=config)
