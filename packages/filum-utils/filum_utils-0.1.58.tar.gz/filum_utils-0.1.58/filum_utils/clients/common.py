import logging
import requests
from json import JSONDecodeError
from requests.auth import HTTPBasicAuth
from filum_utils.errors import BaseError


class BaseClient:
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self._base_url = base_url
        self._username = username
        self._password = password

    def _request(self, method, endpoint, data=None, params=None, timeout: float = None):
        response = requests.request(
            method=method,
            url=self._base_url + endpoint,
            json=data,
            params=params,
            auth=HTTPBasicAuth(self._username, self._password),
            timeout=timeout,
        )

        if response.status_code >= 300:
            logging.error(f"{self.__class__} error: {response.status_code} - {endpoint} - {response.content}")
            raise BaseError(f"Implementation Error", data={
                "method": method,
                "endpoint": endpoint,
                "params": params,
                "status_code": response.status_code,
                "content": str(response.content)
            })
        try:
            return response.json()
        except JSONDecodeError:
            return response.content
