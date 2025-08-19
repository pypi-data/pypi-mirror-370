import os
from pathlib import Path
from typing import Any
from typing import Dict

import httpx

from syrius.exceptions import FlowAPIException


class SyriusAuth(httpx.Auth):
    """ """

    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: httpx.Request) -> httpx.Response:
        """

        :param request: httpx.Request:

        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class SyriusAPI:
    """ """
    api_key: str
    base_url: str

    def __init__(self):
        self.api_key = os.environ.get("SYRIUS_API_KEY")
        self.base_url = os.environ.get("SYRIUS_BASE_URL",
                                       "https://api.exit8.io/api")

    def flow_exist(self, name: str, hash: str) -> bool:
        """

        :param name: str:
        :param hash: str:

        """
        response = httpx.get(
            self._set_url("flow", "name", name, "hash", hash),
            auth=SyriusAuth(self.api_key),
            timeout=None
        )
        if response.status_code == 200:
            return True
        return False

    def add_flow(self, flow: Dict[str, Any]):
        """

        :param flow: Dict[str:
        :param Any]:

        """
        response = httpx.post(self._set_url("flow"),
                              json=flow,
                              auth=SyriusAuth(self.api_key),
                              timeout=None)
        if response.status_code == 200:
            return response.json()
        raise FlowAPIException("Flow add process failed")

    def run(self, name: str, hash: str):
        """

        :param name: str:
        :param hash: str:

        """
        response = httpx.post(
            self._set_url("flow", "name", name, "hash", hash, "run"),
            auth=SyriusAuth(self.api_key),
            timeout=None
        )
        if response.status_code == 200:
            data = response.json()
            return data["runner"]
        raise FlowAPIException("Remote flow server error")

    def check_flow_status(self, runner: str):
        """

        :param runner: str:

        """
        response = httpx.get(self._set_url("flow", "status", runner),
                             auth=SyriusAuth(self.api_key),
                             timeout=None)
        if response.status_code == 200:
            return response.json()
        raise FlowAPIException("remote flow execution failure")

    def upload_file(self, path_file: str):
        """

        :param path_file: str:

        """
        _test_upload_file = Path(path_file)
        _files = {"upload_file": _test_upload_file.open("rb")}
        response = httpx.post(self._set_url("file"),
                              files=_files,
                              auth=SyriusAuth(self.api_key),
                              timeout=None)
        if response.status_code == 200:
            return response.json()
        raise FlowAPIException("impossible to upload files")

    def upload_public_file(self, path_file: str):
        """

        :param path_file: str:

        """
        _test_upload_file = Path(path_file)
        _files = {"upload_file": _test_upload_file.open("rb")}
        response = httpx.post(self._set_url("file", "public"),
                              files=_files,
                              auth=SyriusAuth(self.api_key),
                              timeout=None)
        if response.status_code == 200:
            return response.json()
        raise FlowAPIException("impossible to upload files")

    def _set_url(self, *args) -> str:
        """

        :param *args:

        """
        return os.path.join(self.base_url, *args)
