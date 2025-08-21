# teach/gitea_api/api.py
# ------------------
# Offers an api to gitea. 
# Currently, this api competes with git_backend. The tension 
# reflects uncertainty on whether MWC will support multiple backends. 

import requests
from making_with_code_cli.teach.gitea_api.exceptions import (
    GiteaServerUnavailable,
    RequestFailed,
)

class GiteaTeacherApi:
    """Provides an API to the Gitea instance. 
    Initialize with a username and token, or by default the admin values
    will be used from settings.
    """
    GITEA_URL = "https://git.makingwithcode.org"

    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"

    methods = {
        "GET": requests.get,
        "POST": requests.post, 
        "PATCH": requests.patch,
        "DELETE": requests.delete,
    }
    def __init__(self, debug=False):
        self.debug = debug

    def user_has_repo(self, username, repo_name, token):
        response = self.get(f"/repos/{username}/{repo_name}", username, token)
        return response.ok

    def get_user_repos(self, username, token):
        response = self.get(f"/users/{username}/repos", username, token)
        return response

    def get(self, url, username, token, params=None, sudo=None, check=False):
        return self.authenticated_request(self.GET, url, username, token, params=params, sudo=sudo, check=check)

    def authenticated_request(self, method_name, url, username, token, 
            data=None, params=None, sudo=None, check=True):
        msg = f"Gitea request: {method_name} {url}"
        if data: 
            msg += f" data={data}"
        if params: 
            msg += f" params={params}"
        if data and method_name not in (self.POST, self.PATCH, self.DELETE):
            raise ValueError("Data is only supported on POST, PATCH, or DELETE requests")
        if params and method_name != self.GET:
            raise ValueError("Params are only supported on GET requests")
        args = {
            'url': self.GITEA_URL + "/api/v1" + url,
            'auth': (username, token),
        }
        if data:
            args['data'] = data
        if params:
            args['params'] = params
        if sudo:
            args['headers'] = {'Sudo': sudo}
        method = self.methods[method_name]
        response = method(**args)
        if response.status_code >= 500 or response.status_code == 403:
            raise GiteaServerUnavailable()
        if check and not response.ok:
            raise RequestFailed(response)
        if self.debug:
            print(msg)
            print(response)
        return response
