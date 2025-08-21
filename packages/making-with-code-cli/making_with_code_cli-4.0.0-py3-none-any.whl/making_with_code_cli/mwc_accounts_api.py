import requests
import json
import os
from pathlib import Path
from urllib.parse import urljoin
from getpass import getpass
from making_with_code_cli.errors import MWCError

MWC_ACCOUNTS_SERVER = "https://accounts.makingwithcode.org"

class MWCAccountsAPI:
    def __init__(self, mwc_accounts_server=None):
        self.mwc_accounts_server = mwc_accounts_server or MWC_ACCOUNTS_SERVER

    def login(self, username, password):
        "Authenticates with a username and password, returning an auth token"
        data = {"username": username, "password": password}
        response = self.post("/login", data=data)
        return self.handle_response(response)

    def logout(self, token):
        response = self.post("/logout", token=token)
        return self.handle_response(response)

    def get_status(self, token):
        response = self.get("/status", token=token)
        return self.handle_response(response)

    def get_roster(self, token):
        response = self.get("/roster", token=token)
        return self.handle_response(response)

    def create_student(self, token, params):
        response = self.post("/students", data=params, token=token)
        return self.handle_response(response)

    def update_student(self, token, params):
        response = self.put("/students", data=params, token=token)
        return self.handle_response(response)

    def create_section(self, token, params):
        response = self.post("/sections", data=params, token=token)
        return self.handle_response(response)

    def update_section(self, token, params):
        response = self.put("/sections", data=params, token=token)
        return self.handle_response(response)

    def get(self, url, data=None, token=None):
        return self.http_request("get", url, data=data, token=token)

    def post(self, url, data=None, token=None):
        return self.http_request("post", url, data=data, token=token)

    def put(self, url, data=None, token=None):
        return self.http_request("put", url, data=data, token=token)

    def http_request(self, method, url, data=None, token=None):
        fn = getattr(requests, method)
        headers = {"Authorization": f"Token {token}"} if token else None
        try:
            return fn(self.mwc_accounts_server + url, data=data, headers=headers)
        except requests.exceptions.ConnectionError:
            raise self.ServerError("Could not connect to server")

    def handle_response(self, response):
        if response.ok:
            return response.json()
        elif response.status_code == 500:
            raise self.ServerError("Error 500")
        else:
            try:
                rj = response.json()
                raise self.RequestFailed(rj, data=rj)
            except requests.exceptions.JSONDecodeError:
                raise self.RequestFailed(response)

    class RequestFailed(MWCError):
        def __init__(self, *args, data=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.data = data

    class ServerError(MWCError):
        pass





