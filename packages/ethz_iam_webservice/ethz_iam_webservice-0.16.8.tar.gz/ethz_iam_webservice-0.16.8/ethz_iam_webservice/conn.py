import json
import os
import posixpath
from dataclasses import InitVar, dataclass
from typing import ClassVar
from urllib.parse import urljoin

import requests

from .verbose import VERBOSE

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

@dataclass
class IAMApi:
    admin_username: InitVar[str]
    admin_password: InitVar[str]
    _admin_username: ClassVar[str]
    _admin_password: ClassVar[str]
    hostname: ClassVar[str] = "https://iamws.ethz.ch"
    endpoint_base: ClassVar[str] = "/"
    verify_certificates: ClassVar[bool] = True
    timeout: ClassVar[int] = int(os.environ.get("IAM_TIMEOUT", 240))

    def __post_init__(self, admin_username, admin_password):
        self.__class__._admin_username = admin_username
        self.__class__._admin_password = admin_password

    def get_username(self):
        username = os.environ.get("IAM_USERNAME", "")
        if not username:
            raise ValueError(
                "No IAM_USERNAME env variable found. Please provide an admin username"
            )
        self.__class__._admin_username = username

    def get_password(self):
        password = os.environ.get("IAM_PASSWORD", "")
        if not password:
            raise ValueError(
                "No IAM_PASSWORD env variable found. Please provide an admin password"
            )
        self.__class__._admin_password = password

    def get_auth(self):
        return (self._admin_username, self._admin_password)

    def get_timeout(self) -> int:
        return int(os.environ.get("IAM_TIMEOUT", self.timeout))

    def get_request(self, endpoint):
        full_url = urljoin(self.hostname, posixpath.join(self.endpoint_base, endpoint))
        resp = requests.get(
            full_url,
            headers=DEFAULT_HEADERS,
            auth=self.get_auth(),
            verify=self.verify_certificates,
            timeout=self.get_timeout(),
        )
        if resp.ok:
            return resp.json()
        elif resp.status_code in (401, 403):
            raise PermissionError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        elif resp.status_code == 404:
            try:
                msg = resp.json().get("msg")
            except json.JSONDecodeError:
                raise ValueError("not found")
            raise ValueError(msg)
        else:
            message = resp.json()
            raise ValueError(message)

    def post_request(
        self,
        endpoint,
        body,
        success_msg=None,
        not_allowed_msg=None,
        failed_msg=None,
    ) -> dict:
        full_url = urljoin(self.hostname, posixpath.join(self.endpoint_base, endpoint))
        resp = requests.post(
            full_url,
            json.dumps(body),
            headers=DEFAULT_HEADERS,
            auth=self.get_auth(),
            verify=self.verify_certificates,
            timeout=self.get_timeout(),
        )
        if resp.ok:
            if VERBOSE and success_msg:
                print(success_msg)
            return resp.json()
        elif resp.status_code == 401:
            if not_allowed_msg is None:
                not_allowed_msg = (
                    f"You are NOT ALLOWED to do a POST operation on {endpoint}"
                )
            raise PermissionError(not_allowed_msg)
        elif resp.status_code == 409:
            raise ValueError("Conflict error: the resource already exists or has been recently deleted.")
        elif resp.status_code == 500:
            raise ValueError(
                f"Internal server error while trying to do a POST operation on {endpoint}"
            )
        else:
            data = resp.text
            if not failed_msg:
                failed_msg = f"FAILED to do a POST operation on {endpoint}: {data}"
            raise ValueError(failed_msg)

    def put_request(
        self,
        endpoint,
        body=None,
        success_msg=None,
        not_allowed_msg=None,
        failed_msg=None,
        ignore_errors=False,
    ) -> dict:
        full_url = urljoin(self.hostname, posixpath.join(self.endpoint_base, endpoint))
        if not body:
            body = {}
        resp = requests.put(
            full_url,
            json.dumps(body),
            headers=DEFAULT_HEADERS,
            auth=self.get_auth(),
            verify=self.verify_certificates,
            timeout=self.get_timeout(),
        )
        if resp.ok:
            if resp.content:
                return resp.json()
        if ignore_errors:
            return {}

        if resp.status_code == 401 or resp.status_code == 403:
            if not_allowed_msg is None:
                not_allowed_msg = (
                    f"You are NOT ALLOWED to do a PUT operation on {endpoint}"
                )
            raise PermissionError(not_allowed_msg)
        elif not resp.ok:
            try:
                data = resp.json()
                return data
            except requests.exceptions.JSONDecodeError as exc:
                data = {"msg": str(exc)}
            if not failed_msg:
                failed_msg = (
                    f"FAILED to do a PUT operation on {endpoint}: {data.get('msg')}"
                )
                raise ValueError(failed_msg)
            raise ValueError(data)

    def delete_request(
        self,
        endpoint,
        success_msg=None,
        not_allowed_msg=None,
        failed_msg=None,
    ) -> requests.Response:
        full_url = urljoin(self.hostname, posixpath.join(self.endpoint_base, endpoint))
        resp = requests.delete(
            full_url,
            headers=DEFAULT_HEADERS,
            auth=self.get_auth(),
            verify=self.verify_certificates,
            timeout=self.get_timeout(),
        )

        if resp.ok:
            if VERBOSE and success_msg:
                print(success_msg)
            return resp
        elif resp.status_code == 401:
            if not_allowed_msg is None:
                not_allowed_msg = (
                    f"You are NOT ALLOWED to do a DELETE operation on {endpoint}"
                )
            raise PermissionError(not_allowed_msg)
        else:
            data = resp.json()
            if not failed_msg:
                failed_msg = f"FAILED to do a DELETE operation on {endpoint}"
            raise ValueError(f"{failed_msg}: {data}")


@dataclass
class IAMApiLegacy(IAMApi):
    hostname: ClassVar[str] = "https://iam.password.ethz.ch"
    endpoint_base: ClassVar[str] = "iam-ws-legacy/"

@dataclass
class IAMApiAlternative(IAMApi):
    admin_username: InitVar[str] = ""
    admin_password: InitVar[str] = ""
    hostname: ClassVar[str] = "https://idn.ethz.ch"
    endpoint_base: ClassVar[str] = "usermgr"
