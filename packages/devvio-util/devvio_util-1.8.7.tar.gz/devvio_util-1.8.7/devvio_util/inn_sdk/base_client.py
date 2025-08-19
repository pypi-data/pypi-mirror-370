import requests
import logging
from uuid import uuid4
from typing import Optional


def generate_client_id() -> str:
    return str(uuid4())


class BaseClient:
    def __init__(self, host_url: str, api_key: Optional[str] = None):
        self.host_url = host_url
        self.api_key = api_key or ""
        self.uuid = None
        self.access_token = None
        self.refresh_token = None
        self.id_token = None
        self.username = None
        self.password = None
        self.email = None
        self.pub = None

    def set_uuid(self, uuid):
        self.uuid = uuid

    def set_tokens(self, access_token: str, id_token: str, refresh_token: str = None):
        self.access_token = access_token
        self.id_token = id_token
        if refresh_token:
            self.refresh_token = refresh_token

    def set_username(self, username):
        self.username = username

    def set_email(self, email):
        self.email = email

    def set_apikey(self, apikey):
        self.api_key = apikey

    def _send_post_request(self, url: str, body: dict):
        """
        Send a POST request to a specified URL with JSON data.

        This method sends a POST request to the given `url` concatenated with the
        `host_url`. It includes the provided `body` as JSON data in the request.
        If the response is successful (HTTP status code 200), it parses the JSON
        response and returns it. Otherwise, it raises a RuntimeError with the
        details of the unsuccessful response.

        :param url: The relative URL to which the POST request will be sent.
        :param body: The data to be sent in the request body as JSON.
        :return: The JSON response data returned from the server.
        :raise: RuntimeError: If the response status is not successful (non-200 status).
        """
        my_url = f"{self.host_url}{url}"
        logging.debug(f"URL: {my_url} JSON: {body}")

        headers = (
            {"Authorization": f"Bearer {self.access_token}"}
            if self.access_token
            else {}
        )
        if self.api_key:
            logging.debug(f"Setting {self.api_key=}")
            body["apikey"] = self.api_key
        res = requests.post(my_url, json=body, headers=headers)

        if not res.ok:
            logging.warning(f"request error: {my_url}")
            logging.warning(f"request error: {res.text}")
            res.raise_for_status()

        res_j = res.json()
        logging.debug(f"json_return: {res_j}")
        return res_j

    def _send_get_request(self, url: str):
        """
        Send a POST request to a specified URL with JSON data.

        This method sends a GET request to the given `url` concatenated with the
        `host_url`.
        If the response is successful (HTTP status code 200), it parses the JSON
        response and returns it. Otherwise, it raises a RuntimeError with the
        details of the unsuccessful response.

        :param url: The relative URL to which the GET request will be sent.
        :return: The JSON response data returned from the server.
        :raise: RuntimeError: If the response status is not successful (non-200 status).
        """
        my_url = f"{self.host_url}{url}"
        headers = (
            {"Authorization": f"Bearer {self.access_token}"}
            if self.access_token
            else {}
        )

        res = requests.get(my_url, headers=headers)
        if res.ok:
            res_j = res.json()
        else:
            raise RuntimeError(f"{res}")
        return res_j

    def _send_request(self, url, body=None):
        if body is not None:
            return self._send_post_request(url=url, body=body)
        return self._send_get_request(url=url)
