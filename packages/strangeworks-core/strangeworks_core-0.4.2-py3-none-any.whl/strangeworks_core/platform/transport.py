"""transport.py."""
from typing import Callable, Dict, Optional

import requests
from gql.transport.requests import RequestsHTTPTransport
from requests.adapters import HTTPAdapter, Retry

from strangeworks_core.errors.error import StrangeworksError


class StrangeworksTransport(RequestsHTTPTransport):
    """Transport layer with automatic token refresh."""

    def __init__(
        self,
        api_key: str,
        url: str,
        authenticator: Callable[[str], str],
        auth_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retries: int = 0,
        **kvargs,
    ) -> None:
        """Initialize Transport."""
        self.url = url
        self.api_key = api_key
        super().__init__(
            url=url,
            headers=headers,
            timeout=timeout,
            retries=retries,
        )

        self.authenticator = authenticator
        self.auth_token = auth_token
        self.headers = headers or {}
        if self.auth_token:
            self.headers["Authorization"] = self.auth_token

    def connect(self):
        """Set up a session object.

        Creates a session object for the transport to use and configures retries and
        re-authentication.
        """
        if self.session is None:
            self.session = requests.Session()

            # set up retries.
            if self.retries > 0:
                adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=self.retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=None,
                    )
                )

                for prefix in "http://", "https://":
                    self.session.mount(prefix, adapter)

            # setup token refresh if expired.
            self.session.hooks["response"].append(self._reauthenticate)

        self._refresh_token()

    def _refresh_token(self) -> None:
        self.auth_token = self.authenticator(self.api_key)
        self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def _reauthenticate(self, res: requests.Response, **kwargs) -> requests.Response:
        """Reauthenticate to Strangeworks.

        Parameters
        ----------
        res : requests.Response
        **kwargs

        Returns
        -------
        : requests.Response
        """
        if res.status_code == requests.codes.unauthorized:
            seen_before_header = "X-SW-SDK-Re-Auth"
            # We've tried once before but no luck. Maybe they've changed their api_key?
            if res.request.headers.get(seen_before_header):
                raise StrangeworksError(
                    "Unable to re-authenticate your request. Utilize "
                    "strangeworks.authenticate(api_key) with your most up "
                    "to date credentials and try again."
                )

            self._refresh_token()

            # ensure that the new token is part of the header
            res.request.headers["Authorization"] = f"Bearer {self.auth_token}"
            res.request.headers[seen_before_header] = True
            return self.session.send(res.request)
