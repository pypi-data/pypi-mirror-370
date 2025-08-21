from subprocess import run, CalledProcessError
from making_with_code_cli.helpers import cd

def in_repo():
    """Checks whether currently in repo"""
    try:
        run("git status", shell=True, capture_output=True, check=True)
        return True
    except CalledProcessError:
        return False

def repo_has_changes():
    return len(changed_files()) > 0

def changed_files():
    "Returns a list of (status, filename) tuples for changed files"
    cmd = "git status --porcelain"
    result = run(cmd, shell=True, capture_output=True, text=True).stdout
    files = []
    if result:
        for line in result.split('\n'):
            files.append((line[:2], line[3:]))
        return files
    else:
        return []
