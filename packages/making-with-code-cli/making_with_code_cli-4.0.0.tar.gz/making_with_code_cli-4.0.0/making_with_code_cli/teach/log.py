# teach/log.py
# ---------------
# Implements `mwc teach log`.
# This task iterates over all student repos and clones or pulls them 
# as appropriate.

import click
from git import Repo
from pathlib import Path
from threading import Thread, Semaphore
from textwrap import wrap
import dateparser
from making_with_code_cli.teach.student_repos import StudentRepos
from making_with_code_cli.settings import read_settings
from making_with_code_cli.teach.setup import check_required_teacher_settings
from making_with_code_cli.styles import (
    address,
    question,
    info,
    debug as debug_fmt,
    confirm,
    error,
)

def date_string(arg):
    return dateparser.parse(arg, settings={'RETURN_AS_TIMEZONE_AWARE': True})

@click.command()
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option('-g', "--group", help="Filter by group name")
@click.option('-c', "--course", help="Filter by course name")
@click.option('-u', "--user", help="Filter by username")
@click.option('-n', "--unit", help="Filter by unit name/slug")
@click.option('-m', "--module", help="Filter by module name/slug")
@click.option('-s', "--start", type=date_string, help="Start datetime")
@click.option('-e', "--end", type=date_string, help="End datetime")
@click.option('-U', "--update", is_flag=True, help="Update repos first")
@click.option('-t', "--threads", type=int, default=8, help="Maximum simultaneous threads")
def log(config, group, course, user, unit, module, start, end, update, threads):
    "Show repo logs"
    if update:
        from making_with_code_cli.teach.update import update as update_task
        update_task.callback(config, group, course, user, unit, module, threads)
    settings = read_settings(config)
    if not check_required_teacher_settings(settings):
        return
    repos = StudentRepos(settings, threads)
    get_commits = get_repo_commits_factory(start, end)
    results = repos.apply(get_commits, group=group, course=course, user=user, 
            unit=unit, module=module, status_message="Collecting logs")
    for repo in results:
        click.echo(address('-' * 80))
        click.echo(address(repo['path'], preformatted=True))
        for commit in repo['commits']:
            click.echo(info(format_commit(commit), preformatted=True))

def get_repo_commits_factory(start, end):
    def get_repo_commits(semaphore, results, group, username, path, token):
        "Gets commits from repo"
        semaphore.acquire()
        if path.exists():
            repo = Repo(path)
            commits = []
            for commit in repo.iter_commits():
                if in_bounds(commit.committed_datetime, start, end):
                    commits.append(commit)
            if commits:
                results.append({"path": path, "commits": commits})
        semaphore.release()
    return get_repo_commits

def in_bounds(value, minimum=None, maximum=None):
    return (not minimum or value >= minimum) and (not maximum or value <= maximum)

def format_commit(commit):
    return '\n'.join([
        f"Author: {commit.author}",
        f"Date: {commit.committed_datetime.isoformat()}",
        "",
        '\n'.join('    ' + line for line in commit.message.split('\n'))
    ])

