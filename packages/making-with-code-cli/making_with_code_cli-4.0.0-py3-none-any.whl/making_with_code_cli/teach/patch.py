# teach/patch.py
# ---------------
# Implements `mwc teach patch`.
# This task patches a module for all students in a group. 
# Patching is most useful when a change needs to be applied 
# to a module after a course has started, and students each
# have their own copy of the repo.

import click
import git
from git import Repo
from making_with_code_cli.settings import read_settings
from making_with_code_cli.teach.setup import check_required_teacher_settings
from making_with_code_cli.teach.student_repos import StudentRepos
from making_with_code_cli.teach.update import update as update_task
from making_with_code_cli.styles import success, error

GIT_REMOTE_NAME = "origin"

@click.command()
@click.argument("patch")
@click.argument("group")
@click.argument("module")
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option('-c', "--course", help="Filter by course name")
@click.option('-u', "--user", help="Filter by username")
@click.option('-n', "--no-commit", is_flag=True, help="Commit and push changes")
@click.option('-m', "--message", default="Applying patch", help="Commit message")
@click.option('-t', "--threads", type=int, default=8, help="Maximum simultaneous threads")
def patch(patch, group, module, config, course, user, no_commit, message, threads):
    settings = read_settings(config)
    if not check_required_teacher_settings(settings):
        return
    update_task.callback(config, group, course, user, None, module, threads)
    apply_patch = apply_patch_factory(patch, message, no_commit)
    repos = StudentRepos(settings, threads)
    results = repos.apply(apply_patch, group=group, course=course, module=module, 
            user=user, status_message=f"Applying patch {patch}")
    for result in results:
        if result['success']:
            click.echo(success(f"SUCCESS: {result['path']}", preformatted=True))
        else:
            click.echo(error(f"ERROR: {result['path']}: {result['message']}", preformatted=True))

def apply_patch_factory(patch, commit_message, no_commit=False):
    """Creates a function which will apply a patch to a repo. 
    """
    def apply_patch(semaphore, results, group, username, path, token):
        semaphore.acquire()
        if path.exists():
            repo = Repo(path)
            if has_staged_changes(repo):
                results.append({
                    "path": path, 
                    "success": False, 
                    "message": "Repo has staged changes."
                })
            elif has_unstaged_changes(repo):
                results.append({
                    "path": path, 
                    "success": False, 
                    "message": "Repo has unstaged changes."
                })
            else:
                try:
                    repo.git.apply(patch)
                except git.exc.GitCommandError as e:
                    results.append({"path": path, "success": False, "message": str(e)})
                    return
                if not no_commit:
                    try:
                        repo.git.add(update=True)
                        repo.index.commit(commit_message)
                        remote = repo.remote(name=GIT_REMOTE_NAME)
                        remote.push()
                    except Exception as e:
                        results.append({"path": path, "success": False, "message": str(e)})
                        return
                results.append({"path": path, "success": True})
        semaphore.release()
    return apply_patch

def has_staged_changes(repo):
    staged_changes = repo.index.diff("HEAD")
    return len(staged_changes) > 0

def has_unstaged_changes(repo):
    unstaged_changes = repo.index.diff(None)
    return len(unstaged_changes) > 0


