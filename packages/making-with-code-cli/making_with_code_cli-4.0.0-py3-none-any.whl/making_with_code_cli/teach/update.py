# teach/update.py
# ---------------
# Implements `mwc teach update`.
# This task iterates over all student repos and clones or pulls them 
# as appropriate.

import os
import click
from pathlib import Path
from making_with_code_cli.settings import read_settings
from making_with_code_cli.teach.setup import check_required_teacher_settings
from making_with_code_cli.teach.student_repos import StudentRepos
from making_with_code_cli.teach.student_repo_functions import (
    update_repo,
)
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.teach.gitea_api.api import GiteaTeacherApi
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
@click.option("--section", help="Filter by section slug")
@click.option("--course", help="Filter by course name")
@click.option("--user", help="Filter by username")
@click.option("--unit", help="Filter by unit name/slug")
@click.option("--module", help="Filter by module name/slug")
@click.option("--threads", type=int, default=8, help="Maximum simultaneous threads")
def update(config, section, course, user, unit, module, threads):
    "Update student repos"
    settings = read_settings(config)
    if not check_required_teacher_settings(settings):
        return
    repos = StudentRepos(settings, threads)
    results = repos.apply(update_repo, section=section, course=course, user=user, 
            unit=unit, module=module, status_message="Updating repos")
    for result in results:
        if result['process'].returncode != 0:
            click.echo(error('-' * 80))
            click.echo(error(result['path'], preformatted=True))
            click.echo(error(result['process'].stdout, preformatted=True))

