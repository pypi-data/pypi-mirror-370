from typing import Optional

import requests
from requests.auth import HTTPBasicAuth


def default_on_response(response: requests.Response) -> Optional[dict]:
    """
    :param response:
    :return: the input response
    :raise HTTPError: if status_code is not OK(200)
    """
    if response.status_code != 200:
        response.raise_for_status()
    else:
        return response.json()


class Request:
    def __init__(self, auth: dict = None, on_response=default_on_response):
        self.options: dict = {"headers": {}}
        if auth is not None:
            bearer = auth.get("bearer")
            if bearer is not None:
                self.options["headers"]["Authorization"] = f"Bearer {bearer}"
                del auth["bearer"]
            else:
                self.options["auth"] = HTTPBasicAuth(auth["username"], auth["password"])
        self.on_response = on_response

    def request(self, url, method: str, params=None, data=None, json=None) -> dict:
        response = requests.request(
            method, url, params=params, data=data, json=json, **self.options
        )
        return self.on_response(response)
