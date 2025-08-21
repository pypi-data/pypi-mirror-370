from pathlib import Path
from subprocess import run, CalledProcessError
import click
from making_with_code_cli.helpers import cd
from making_with_code_cli.setup.tasks import WORK_DIR_PERMISSIONS
from making_with_code_cli.styles import (
    address,
    info,
    confirm,
    error,
)

class GitBackend:
    """Base class interface to backend git server.
    All Making With Code deployments are backed by a git server, but the nature of the
    server and the strategies for completing tasks vary by backend. 
    """

    def __init__(self, settings):
        self.settings = settings

    def init_module(self, module, modpath):
        raise NotImplemented()

    def update(self, module, modpath, install=True):
        if (modpath / ".git").is_dir():
            with cd(modpath):
                relpath = self.relative_path(modpath)
                try:
                    click.echo(address(f"Checking {relpath} for updates.", preformatted=True))
                    gitresult = run("git pull", shell=True, check=True, capture_output=True,
                            text=True)
                    click.echo(info(gitresult.stdout))
                    if install and Path("pyproject.toml").exists():
                        result = run("poetry install", shell=True, check=True, 
                                capture_output=True, text=True)
                        click.echo(info(result.stdout, preformatted=True))
                except CalledProcessError as e:
                    click.echo(error(f"There was a problem updating {relpath}. Ask a teacher."))
                    raise e

    def work_dir(self):
        return Path(self.settings['work_dir'])

    def relative_path(self, path):
        return path.relative_to(self.work_dir())

