from pathlib import Path
from enum import Flag, auto
from stat import *
import sys
import os
import re
import platform
from importlib.util import find_spec
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.styles import (
    address,
    question,
    debug,
    confirm,
    info,
    success,
    warn,
    error,
)
from making_with_code_cli.curriculum import (
    get_curriculum,
)
from making_with_code_cli.errors import (
    CurriculumSiteNotAvailable,
    NoCurriculaAvailable,
    SoftwareInstallationError,
)
import click
import requests
from subprocess import run
import yaml

INTRO_MESSAGE = (
    "Welcome to Making with Code setup. This program will ask you for some settings "
    "and make sure all the required software is installed on your computer. "
    "Some of the steps may take a while to complete. "
    "A few notes:"
)
INTRO_NOTES = [
    "You can re-run this script if you want to make any changes.",
    "You can quit this program by pressing Control + C at the same time.",
    "Many questions have default values, shown in [brackets]. Press enter to accept the default.",
    "The setup may ask for your password. As a security measure, you won't see any characters when you type it in.",
    "If you get stuck or have any questions, ask a teacher.",
]
WORK_DIR_PERMISSIONS = S_IRWXU | S_IXGRP | S_IXOTH

class PlatformNotSupported(Exception):
    def __init__(self):
        err = "This platform is not supported."
        return super().__init__(err)

class Platform(Flag):
    MAC = auto()
    UBUNTU = auto()
    SUPPORTED = MAC | UBUNTU 
    UNSUPPORTED = 0

    @classmethod
    def detect(cls):
        system_name = platform.system()
        if system_name == "Darwin":
            return cls.MAC
        if system_name == "Linux":
            return cls.UBUNTU
        return cls.UNSUPPORTED

    @classmethod
    def package_manager(cls, brew_cask=False):
        """Returns the command for the platform's package manager.
        """
        platform = cls.detect()
        if platform == cls.MAC:
            if brew_cask: 
                return "brew install --cask "
            else:
                return "brew install "
        elif platform == cls.UBUNTU:
            return "sudo apt install "
        else:
            raise cls.NotSupported()

def default_work_dir(teacher=False):
    dirname = "making_with_code_teacher" if teacher else "making_with_code"
    if (Path.home() / "Desktop").exists():
        return Path.home() / "Desktop" / dirname
    else:
        return Path.home() / dirname

def choose_mwc_username(default=None):
    """Asks the user to choose their MWC username."""
    return click.prompt(
        question("What is your MWC username?"),
        default=default
    )

def prompt_mwc_password(username, api):
    "Asks for the password. Returns a token when successful."
    while True:
        password = click.prompt(question("What is your MWC password?"), hide_input=True)
        try:
            response = api.login(username, password)
            return response['token']
        except api.RequestFailed:
            click.echo(error(f"Sorry, that's not the right password for {username}."))

def choose_work_dir(default=None, teacher=False):
    """Asks the user to choose where to save their work. 
    Loops until a valid choice is made, prompts if the directory is to be created, 
    and sets file permissions to 755 (u+rwx, g+x, o+x).
    """
    if teacher:
        prompt_text = "Where do you want to save MWC student repositories?"
    else:
        prompt_text = "Where do you want to save your MWC work?"
    while True:
        work_dir = click.prompt(
            question(prompt_text),
            default=default or default_work_dir(teacher=teacher),
            type=click.Path(path_type=Path),
        )
        work_dir = work_dir.expanduser()
        if work_dir.is_file():
            click.echo(error("There's already a file at that location."))
        elif work_dir.exists():
            work_dir.chmod(WORK_DIR_PERMISSIONS)
            return work_dir
        elif click.confirm(confirm("This directory doesn't exist. Create it?")):
            work_dir.mkdir(mode=WORK_DIR_PERMISSIONS, parents=True)
            return work_dir

def choose_mwc_site_url(default=None):
    """Asks the user for the Making With Code site URL
    """
    while True:
        url = click.prompt(
            question("What's the URL of your Making With Code website?"),
            default=default,
        )
        if url.endswith('/'):
            url = url[:-1]
        try:
            curriculum = get_curriculum({'mwc_site_url': url})
            return url
        except CurriculumSiteNotAvailable as err:
            click.echo(error(str(err)))
        except requests.exceptions.MissingSchema as e:
            click.echo(error(str(e)))

def choose_course(options, default=None):
    """Asks the user which course they are part of"""
    if len(options) == 0:
        err = "There is a problem with the MWC site. Please ask a teacher for help."
        click.echo(error(err))
        raise NoCurriculaAvailable(err)
    elif len(options) == 1:
        if default and default not in options:
            confirm(f"Changing your course from '{default}' to '{options[0]}'")
        else:
            confirm(f"You are part of the course '{options[0]}'.")
        return options[0]
    else:
        if default and default not in options:
            confirm(f"Your course was '{default}' but this is no longer available.")
            return click.prompt(
                question("Choose your course:"), 
                type=click.Choice(options),
            )  
        else:
            return click.prompt(
                question("Choose your course:"), 
                default=default,
                type=click.Choice(options),
            )  

def choose_editor(default=None):
    """Asks the user which editor they want to use."""
    while True:
        ed = click.prompt(
            question("Which code editor do you want to use?"),
            default=default
        )
        if editor_installed(ed) or ed in ['atom', 'subl', 'charm', 'mate', 'code']:
            return ed
        click.echo(error(f"Couldn't find {ed}. Double-check that it's installed."))

def editor_installed(ed):
    return bool(run(f"which {ed}", shell=True, capture_output=True).stdout)

def get_shell_name():
    shellpath = run("echo $SHELL", shell=True, capture_output=True, text=True)
    return shellpath.stdout.split('/')[-1].strip()

def get_mwc_rc_path():
    return (Path.home() / ".mwc_rc").resolve()

def platform_rc_file():
    shell = get_shell_name()
    candidates = [
        ("bash", Path.home() / ".bash_profile"),
        ("bash", Path.home() / ".bash_rc"),
        ("bash", Path.home() / ".bashrc"),
        ("zsh", Path.home() / ".zprofile"),
        ("zsh", Path.home() / ".zshrc"),
    ]
    for sh, rc in candidates:
        if shell == sh and rc.exists():
            return rc
    raise IOError("Can't find an rc file.")

class SetupTask:
    "An idempotent task"
    platform = Platform.SUPPORTED
    description = "A task"

    def __init__(self, settings, debug=False):
        self.settings = settings
        self.debug = debug

    def run_task_if_needed(self):
        if Platform.detect() & self.platform:
            if self.is_complete():
                self.report_not_needed()
            else:
                self.run_task()
                self.report_complete()
        
    def is_complete(self):
        return True    

    def run_task(self):
        pass

    def report_not_needed(self):
        click.echo(info(f"{self.description} is already complete."))
        
    def report_complete(self):
        click.echo(success(f"{self.description} is complete!"))

    def debug_log(self, message):
        if self.debug:
            click.echo(debug(message))

    def executable_on_path(self, name):
        return bool(run(f"which {name}", shell=True, capture_output=True).stdout)

# DEPRECATED
class MWCShellConfig(SetupTask):
    """Writes a line in the rc shell config file sourcing ~/.mwc_rc.
    """
    description = "Link main shell config file to ~/.mwc_rc"

    def is_complete(self):
        return f"source {get_mwc_rc_path()}" in platform_rc_file().read_text()

    def run_task(self):
        rc_file = platform_rc_file()
        self.debug_log(f"Adding `mwc` path to {rc_file}")
        with rc_file.open('a') as fh:
            result = run("which mwc", shell=True, check=True, text=True, capture_output=True)
            mwcpath = Path(result.stdout).parent
            fh.write(f"\n# MAKING WITH CODE\n")
            fh.write(f'export PATH="$PATH:{mwcpath}"\n')
            fh.write(f"source {get_mwc_rc_path()}\n")

class InstallXCode(SetupTask):
    description = "Install XCode"
    platform = Platform.MAC

    def is_complete(self):
        return bool(run("xcode-select -p", shell=True, capture_output=True, check=True).stdout)

    def run_task(self):
        msg = (
            "Installing Xcode... (this may take a while)"
            "Please click \"Install\" and accept the license agreement. "
        )
        click.echo(address(msg))
        run("xcode-select --install", shell=True, check=True)

class InstallPoetry(SetupTask):
    description = "Install poetry"

    def is_complete(self):
        if self.executable_on_path("poetry"):
            self.check_for_poetry2()
            return True

    def run_task(self):
        click.echo(address("Installing poetry..."))
        run("pipx install poetry", shell=True, check=True)
        run("poetry self add poetry-plugin-shell", shell=True, check=True)
        self.check_for_poetry2()
        click.echo(address("Installing poetry tab completions..."))
        shell = get_shell_name()
        try:
            if shell == "bash":
                run("poetry completions bash > ~/.bash_completion", shell=True, check=True)
            if shell == "zsh":
                tab_completion_dir = Path("~/.zfunc")
                tab_completion_dir.mkdir(exist_ok=True)
                run("poetry completions zsh > ~/.zfunc/_poetry", shell=True, check=True)
        except PermissionError:
            click.echo(warn(f"Couldn't install tab completions for poetry. This is not a big deal."))

    def check_for_poetry2(self, upgrade=True):
        result = run("poetry --version", shell=True, check=True, capture_output=True, text=True)
        match = re.search(r"(\d+)\.\d+\.\d+", result.stdout)
        if match:
            poetry_major_version = int(match.group(1))
            if not poetry_major_version == 2:
                if upgrade:
                    click.echo(info("Upgrading Poetry"))
                    run("pipx upgrade poetry", shell=True, check=True)
                    run("poetry self add poetry-plugin-shell", shell=True, check=True)
                    self.check_for_poetry2(upgrade=False)
                else:
                    raise MWCInstallationError("Poetry 2 is required. Please upgrade.")
        else:
            raise MWCInstallationError("Could not determine Poetry version; Poetry 2 is required.")

class WriteShellConfig(SetupTask):
    description = "Write the MWC shell configuration file ~/.mwc_rc"

    def is_complete(self):
        p = get_mwc_rc_path()
        return p.exists() and p.read_text() == self.generate_shell_config()

    def run_task(self):
        click.echo(address("Writing the MWC shell configuration file..."))
        mwc_rc_path = get_mwc_rc_path()
        config_text = self.generate_shell_config()
        self.debug_log(f"Writing to {mwc_rc_path}:\n\n{config_text}\n\n")
        mwc_rc_path.write_text(config_text)
        run(f"source {get_mwc_rc_path()}", shell=True, check=True)

    def generate_shell_config(self):
        "Generates the shell configuration file contents"
        f = ""
        shell = get_shell_name()
        f += "# Making With Code RC File\n\n" 
        if Platform.detect() == Platform.MAC:
            if self.settings['editor'] == "subl":
                f += "## Add subl to $PATH\n"
                subldir = "/Applications/Sublime Text.app/Contents/SharedSupport/bin"
                f += f'export PATH="{subldir}:$PATH"\n\n'
        shell = get_shell_name()
        if shell == "zsh": 
            f += "fpath+=~/.zfunc\n"
            f += "autoload -Uz compinit && compinit\n"
        return f

class InstallPackage(SetupTask):
    """A subclass of SetupTask for packages to be installed by the Platform package manager.
    """
    executable_name = "package"
    brew_name = "package"
    apt_name = "package"
    nix_name = "package"
    brew_cask = False

    def __init__(self, *args, **kwargs):
        self.description = f"Install {self.executable_name}"
        super().__init__(*args, **kwargs)

    def is_complete(self):
        return self.executable_on_path(self.executable_name)

    def get_package_name(self):
        system_platform = Platform.detect()
        if system_platform == Platform.MAC:
            return self.brew_name
        elif system_platform == Platform.UBUNTU:
            return self.apt_name
        else:
            raise PlatformNotSupported()
    
    def run_task(self):
        click.echo(address(f"Installing {self.executable_name}..."))
        package_manager = Platform.package_manager(brew_cask=self.brew_cask)
        package_name = self.get_package_name()
        self.debug_log(f"Running: {package_manager}{package_name}")
        run(f"{package_manager}{package_name}", shell=True, check=True)

class InstallGit(InstallPackage):
    platform = Platform.MAC | Platform.UBUNTU
    executable_name = brew_name = apt_name = "git"

class InstallTree(InstallPackage):
    executable_name = brew_name = apt_name = nix_name = "tree"

class InstallVSCode(InstallPackage):
    platform = Platform.MAC
    executable_name = "code"
    brew_name = "visual-studio-code"
    cask = True

    def run_task(self):
        platform = Platform.detect()
        if platform & Platform.UBUNTU:
            run("sudo snap install --classic code", shell=True, check=True)
        else:
            return super().run_task()

class InstallImageMagick(InstallPackage):
    executable_name = "magick"
    brew_name = apt_name = nix_name = "imagemagick"

    def is_complete(self):
        return self.executable_on_path("magick") or self.executable_on_path("convert")

class InstallHttpie(InstallPackage):
    executable_name = "http"
    brew_name = apt_name = nix_name = "httpie"

class InstallScipy(InstallPackage):
    executable_name = brew_name = apt_name = nix_name = "scipy"

    def is_complete(self):
        return find_spec("scipy") is not None

class GitConfiguration(SetupTask):
    """Configure global git settings.
    Can be skipped by setting `skip_git_config: true` in settings.
    """
    description = "Configure git"

    editorcmds = {
        "atom": '"atom --wait"',
        "code": '"code --wait"',
        "subl": '"subl -n -w"',
        "mate": '"mate -w"',
        "vim": "vim",
        "emacs": "emacs",
    }

    def is_complete(self):
        if self.settings.get("skip_git_config"):
            confirm("Skipping git configuration because 'skip_git_config' is set in MWC settings")
            return True
        for key, value in self.get_expected_git_config().items():
            expected = value.strip().strip('"')
            observed = self.read_git_config(key).strip().strip('"')
            if expected != observed:
                return False
        return True

    def run_task(self):
        (Path.home() / ".gitconfig").touch()
        for key, val in self.get_expected_git_config().items():
            run(f'git config --global --replace-all {key} {val}', shell=True, check=True)

    def read_git_config(self, setting):
        "Reads current git config setting"
        result = run(f"git config --get {setting}", shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def get_expected_git_config(self):
        """Returns a dict containing expected git configuration settings.
        """
        git_config = {"init.defaultBranch": "main"}
        if self.settings.get('editor') in self.editorcmds:
            git_config["core.editor"] = self.editorcmds[self.settings.get('editor')]
        git_config["user.name"] = self.settings.get('git_name', self.settings['mwc_username'])
        git_config["user.email"] = self.settings.get('git_email', 'nobody@makingwithcode.org')
        return git_config


