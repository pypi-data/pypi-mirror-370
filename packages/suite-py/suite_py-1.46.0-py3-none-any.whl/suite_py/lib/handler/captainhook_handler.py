# -*- encoding: utf-8 -*-
import requests

from suite_py.__version__ import __version__
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.okta_handler import Okta


class UnauthorizedError(Exception):
    def __init__(self) -> None:
        super().__init__("Unauthorized with captainhook")


class CaptainHook:
    _okta: Okta
    _github: GithubHandler

    def __init__(self, config, okta: Okta, tokens=None):
        self._baseurl = config.user["captainhook_url"]
        self._timeout = config.user["captainhook_timeout"]
        self._okta = okta

        if tokens is not None:
            self._github = GithubHandler(tokens)

    def lock_project(self, project, env):
        data = {
            "project": project,
            "status": "locked",
            "user": self._get_user(),
            "environment": env,
        }
        return self.send_post_request("/projects/manage-lock", data)

    def unlock_project(self, project, env):
        data = {
            "project": project,
            "status": "unlocked",
            "user": self._get_user(),
            "environment": env,
        }
        return self.send_post_request("/projects/manage-lock", data)

    def status(self, project, env):
        return self.send_get_request(
            f"/projects/check?project={project}&environment={env}"
        )

    def check(self):
        return requests.get(f"{self._baseurl}/", timeout=(2, self._timeout))

    def get_users_list(self):
        return self.send_get_request("/users/all")

    def send_metrics(self, metrics):
        self.send_post_request("/suite_py/metrics/", json=metrics).raise_for_status()

    def send_post_request(self, endpoint, data=None, json=None):
        r = requests.post(
            f"{self._baseurl}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json,
            timeout=self._timeout,
        )

        return self._response(r)

    def send_put_request(self, endpoint, data=None, json=None):
        r = requests.put(
            f"{self._baseurl}{endpoint}",
            headers=self._headers(),
            data=data,
            json=json,
            timeout=self._timeout,
        )

        return self._response(r)

    def send_get_request(self, endpoint):
        r = requests.get(
            f"{self._baseurl}{endpoint}",
            headers=self._headers(),
            timeout=(2, self._timeout),
        )

        return self._response(r)

    def _response(self, response):
        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def set_timeout(self, timeout):
        self._timeout = timeout

    def _get_user(self):
        return self._github.get_user().login

    def _headers(self):
        id_token = self._okta.get_id_token()
        return {
            "User-Agent": f"suite-py/{__version__}",
            "Authorization": f"Bearer {id_token}",
        }
