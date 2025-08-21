import os
from subprocess import run
from git import Repo
from making_with_code_cli.teach.gitea_api.api import GiteaTeacherApi
from making_with_code_cli.helpers import in_bounds

MWC_GIT_PROTOCOL = "https"
MWC_GIT_SERVER = "git.makingwithcode.org"

def run_in_repo(command, cwd):
    return run(command, cwd=cwd, shell=True, capture_output=True, text=True)

def update_repo(semaphore, results, section, username, begin, end, path, token):
    semaphore.acquire()
    git_api = GiteaTeacherApi()
    if path.exists():
        process = run_in_repo("git pull", path)
        results.append({"action": "pull", "path": path, "process": process})
    elif git_api.user_has_repo(username, path.name, token):
        os.makedirs(path.parent, exist_ok=True)
        url = (
            f"{MWC_GIT_PROTOCOL}://{username}:{token}@{MWC_GIT_SERVER}/"
            f"{username}/{path.name}.git"
        )
        process = run_in_repo(f"git clone {url}", path.parent)
        results.append({"action": "clone", "path": path, "process": process})
    semaphore.release()

def count_commits(semaphore, results, section, username, begin, end, path, token):
    "Counts commits in repo"
    semaphore.acquire()
    if path.exists():
        repo = Repo(path)
        commits = repo.iter_commits(reverse=True)
        first_commit = next(commits)
        n = 0
        for commit in commits:
            if in_bounds(commit.committed_datetime, begin, end):
                n += 1
        results.append({
            "section": section, 
            "username": username, 
            "module": path.name, 
            "score": n, 
        })
    semaphore.release()

def count_changed_py_lines(semaphore, results, section, username, begin, end, path, token):
    "Counts lines changed in Python files across all commits in repo"
    semaphore.acquire()
    if path.exists():
        repo = Repo(path)
        changed_lines = 0
        commits = repo.iter_commits(reverse=True)
        first_commit = next(commits)
        for commit in commits:
            if in_bounds(commit.committed_datetime, begin, end):
                for f, stats in commit.stats.files.items():
                    if f.endswith(".py"):
                        changed_lines += stats['lines']
        results.append({
            "section": section, 
            "username": username, 
            "module": path.name, 
            "score": changed_lines
        })
    semaphore.release()

def count_changed_md_lines(semaphore, results, section, username, begin, end, path, token):
    "Counts lines changed in Python files across all commits in repo"
    semaphore.acquire()
    if path.exists():
        repo = Repo(path)
        changed_lines = 0
        commits = repo.iter_commits(reverse=True)
        first_commit = next(commits)
        for commit in commits:
            if in_bounds(commit.committed_datetime, begin, end):
                for f, stats in commit.stats.files.items():
                    if f.endswith(".md"):
                        changed_lines += stats['lines']
        results.append({
            "section": section, 
            "username": username, 
            "module": path.name, 
            "score": changed_lines
        })
    semaphore.release()

def module_completion(semaphore, results, section, username, begin, end, path, token):
    "Returns a [0..1] ratio of module completion, based on tests."
    semaphore.acquire()
    if path.exists():
        results.append({
            "section": section, 
            "username": username, 
            "module": path.name, 
            "score": 0
        })
    semaphore.release()

