from __future__ import annotations

import json
import logging
import re
from base64 import b64decode
from datetime import datetime

import requests
import urllib3

from vectice.__version__ import __vectice_version__, __version__

DEFAULT_API_ENDPOINT = "https://app.vectice.com"


def default_http_headers() -> dict[str, str]:
    return {"Vectice-SDK-Version": __version__, "Vectice-Version": __vectice_version__}


def format_url(url: str) -> str:
    """Add HTTPS protocol if missing and remove trailing slash.

    Parameters:
        url: The URL to format.

    Returns:
        The formatted URL.
    """
    url = url.rstrip("/")
    if not re.match("(?:http|https|ftp)://", url):
        return "https://{}".format(url)
    return url


_logger = logging.getLogger(__name__)


class Auth:  # nosec B107
    def __init__(
        self,
        api_endpoint: str,
        api_token: str,
    ):
        self._default_request_headers: dict[str, str] = default_http_headers()
        self._API_TOKEN = api_token
        self._API_BASE_URL = format_url(api_endpoint)
        self.verify_certificate = False
        self._jwt: str | None = None
        self._jwt_expiration: int | None = None
        urllib3.disable_warnings()
        self._refresh_token()

    @property
    def _token(self) -> str | None:
        if self._jwt_expiration is None:
            return None
        # Refresh token 1 min before expiration
        if datetime.now().timestamp() >= self._jwt_expiration - 60:
            self._refresh_token()
        return self._jwt

    @_token.setter
    def _token(self, jwt: str) -> None:
        self._jwt = jwt
        self._jwt_expiration = self._get_jwt_expiration(jwt)
        self._default_request_headers["Authorization"] = "Bearer " + jwt

    def _refresh_token(self) -> None:
        _logger.debug("Vectice: Refreshing token... ")
        url = self._API_BASE_URL + "/metadata/authenticate"
        data = '{"apiKey":  "%s" }' % self._API_TOKEN
        headers = {**self._default_request_headers, "Content-Type": "application/json"}
        try:
            response = requests.post(url=url, data=data, verify=self.verify_certificate, headers=headers)  # noqa: S113
            if response.status_code == 200:
                self._token = response.json()["token"]
                _logger.debug("Vectice successfully connected.")
            elif response.status_code == 401:
                raise ConnectionRefusedError("The API token provided is not valid.")
            else:
                raise ValueError(response.text)
        except requests.ConnectionError:
            raise ConnectionError(
                f"Host {self._API_BASE_URL} is not reachable, if you are running your own instance of vectice please indicate it with the host parameter of connect function. You can find more information here : https://docs.vectice.com"
            ) from None

    @staticmethod
    def _get_jwt_expiration(jwt: str) -> int:
        jwt_payload = jwt.split(".")[1]
        jwt_payload_with_padding = f"{jwt_payload}{'=' * (4 - len(jwt_payload) % 4)}"
        return int(json.loads(b64decode(jwt_payload_with_padding))["exp"])

    @property
    def api_base_url(self) -> str:
        return self._API_BASE_URL

    @property
    def http_headers(self) -> dict[str, str]:
        # ensure token is up to date
        self._token  # noqa: B018
        return self._default_request_headers
