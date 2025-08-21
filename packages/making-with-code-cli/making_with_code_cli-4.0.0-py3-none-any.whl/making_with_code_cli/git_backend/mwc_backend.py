from .base_backend import GitBackend
from subprocess import run
from pathlib import Path
from urllib.parse import urlparse
import click
import json
import os
import requests
from making_with_code_cli.helpers import cd
from making_with_code_cli.styles import (
    confirm,
)
from making_with_code_cli.errors import (
    MissingSetting,
    GitServerNotAvailable,
)

class MWCBackend(GitBackend):
    """A Github backend. Students own their own repos and grant teachers access via token.
    Note that this gives the teacher account access to the student's entire github account, 
    within scope.
    """

    MWC_GIT_PROTOCOL = "https"
    MWC_GIT_SERVER = "git.makingwithcode.org"
    COMMIT_TEMPLATE = ".commit_template"

    def init_module(self, module, modpath):
        """Creates the named repo from a template. 
        """
        self.check_settings()
        server, repo_owner, repo_name = self.parse_repo_url(module["repo_url"])

        if modpath.exists():
            self.relocate_existing_directory(modpath)
        if not self.user_has_repo(repo_name):
            self.create_from_template(repo_owner, repo_name)
        with cd(modpath.parent):
            self.clone_repo(repo_name)
        if (modpath / self.COMMIT_TEMPLATE).exists():
            with cd(modpath):
                run(f"git config commit.template {self.COMMIT_TEMPLATE}", shell=True, check=True)

    def user_has_repo(self, repo_name, username=None):
        """Checks to see whether a user already has the named repo.
        """
        username = username or self.settings['mwc_username']
        url = f"/repos/{username}/{repo_name}"
        response = self.authenticated_mwc_request('get', url)
        return response.ok

    def create_from_template(self, template_owner, template_name):
        url = f"/repos/{template_owner}/{template_name}/generate"
        data = {
            "name": template_name,
            "owner": self.settings['mwc_username'],
            "git_content": True
        }
        response = self.authenticated_mwc_request('post', url, data=data)
        return response

    def clone_repo(self, repo_name):
        user = self.settings['mwc_username']
        auth = user + ':' + self.settings['mwc_git_token']
        url = f"{self.MWC_GIT_PROTOCOL}://{auth}@{self.MWC_GIT_SERVER}/{user}/{repo_name}.git"
        run(f"git clone {url}", shell=True, check=True, capture_output=True)

    def check_settings(self):
        if "mwc_username" not in self.settings:
            raise MissingSetting('mwc_username')
        if "mwc_git_token" not in self.settings:
            raise MissingSetting('mwc_git_token')

    def parse_repo_url(self, url):
        """Parses a MWC url like "https://git.makingwithcode.org/mwc/lab_pipes.git"
        Returns ("https://git.makingwithcode.org", "mwc", "lab_pipes")
        """
        result = urlparse(url)
        server = f"{result.scheme}://{result.netloc}"
        path, suffix = result.path.split('.')
        repo_owner, repo_name = path.strip('/').split('/')
        return (server, repo_owner, repo_name)

    def authenticated_mwc_request(self, method_name, urlpath, data=None, params=None):
        server = self.MWC_GIT_PROTOCOL + '://' + self.MWC_GIT_SERVER
        args = {
            'url': server + "/api/v1" + urlpath,
            'auth': (self.settings['mwc_username'], self.settings['mwc_git_token']),
        }
        if data:
            args['data'] = data
        if params:
            args['params'] = params
        method = getattr(requests, method_name)
        response = method(**args)
        if response.status_code >= 500 or response.status_code == 403:
            raise GitServerNotAvailable(server)
        return response

    def relocate_existing_directory(self, path):
        """Moves an existing directory out of the way.
        """
        new_path = path.parent / path.name + '_old'
        while new_path.exists():
            new_path = new_path.parent / new_path.name + '_old'
        click.echo(confirm(f"Moving existing directory {path} to {new_path}."))
        os.rename(path, new_path)
