import click
from subprocess import run, CalledProcessError
from making_with_code_cli.git_wrapper import (
    in_repo,
    repo_has_changes,
)
from making_with_code_cli.styles import (
    address,
    question,
    info,
    debug as debug_fmt,
    confirm,
    error,
)

@click.command()
def submit():
    """Submit your work.
    (This is a wrapper for the basic git workflow.)
    """
    if not in_repo():
        click.echo(error("You are not in a lab, problem set, or project folder."))
        return
    if not repo_has_changes():
        click.echo(info("Everything is already up to date."))
        return
    run("git add --all", shell=True, capture_output=True, check=True)
    run("git --no-pager diff --staged", shell=True, check=True)
    if not click.confirm(address("Here are the current changes. Looks OK?")):
        click.echo(info("Cancelled the submit for now."))
        return
    click.echo(info("Write your commit message, then save and exit the window..."))
    run("git commit", shell=True, capture_output=True, check=True)
    run("git push", shell=True, capture_output=True, check=True)
    click.echo(address("Nice job! All your work in this module has been submitted."))


