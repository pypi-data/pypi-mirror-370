"""client.py."""

import functools
from urllib.parse import urljoin

import requests

from .auth import Authenticator

_SEEN_BEFORE_HEADER = "X-SW-SDK-Re-Auth"


class StrangeworksSession(requests.Session):
    """Next-Gen Rest Client"""

    def __init__(
        self,
        host: str,
        api_key: str,
        authenticator: Authenticator,
    ):
        """Initialize StrangeworksSession Object.

        Parameters
        ----------
        host: str
            The base url for the platform api. Typically https://api.strangeworks.com
        api_key: str
            The api key from the users workspace.
        """
        super().__init__()
        self.host: str = host
        self.api_key: str = api_key
        self._auth = authenticator
        self.headers = {
            "X-Strangeworks-API-Version": "0",
            "X-Strangeworks-Client-ID": "strangeworks-sdk-python",
        }
        self.hooks["response"].append(self._reauth)
        self._refresh_auth_token()

    def _refresh_auth_token(self) -> str:
        token: str = self._auth(self.api_key)
        self.headers["Authorization"] = f"Bearer {token}"
        return token

    def _reauth(self, res: requests.Response, **kwargs) -> requests.Response:
        if res.status_code == requests.codes.unauthorized:
            if res.request.headers.get(_SEEN_BEFORE_HEADER):
                raise Exception(
                    "Unable to re-authenticate your request. Utilize "
                    "strangeworks.authenticate(api_key) with your most up "
                    "to date credentials and try again."
                )
            token: str = self._refresh_auth_token()
            res.request.headers["Authorization"] = f"Bearer {token}"

            res.request.headers[_SEEN_BEFORE_HEADER] = "True"
            return self.send(res.request)
        return res

    def request(self, method, url, headers=None, **kwargs):
        _url: str = str(url)
        if not _url.startswith(self.host):
            _url = urljoin(self.host, str(url))
        if headers:
            headers |= self.headers
        return super().request(method=method, url=_url, headers=headers, **kwargs)


@functools.lru_cache()
def get_session(*, host_url: str, api_key: str):
    """SDK session for a Host URL and API Key."""
    return StrangeworksSession(host=host_url, api_key=api_key)
