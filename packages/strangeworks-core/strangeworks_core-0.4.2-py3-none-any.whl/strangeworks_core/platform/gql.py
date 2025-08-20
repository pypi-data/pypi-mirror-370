"""platform.py."""

from enum import Enum
from typing import Any, Dict, List, Optional
from urllib import parse

from gql import Client, gql
from gql.transport.exceptions import TransportQueryError

from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.platform.auth import (
    PRODUCT_AUTH_URL,
    SDK_AUTH_URL,
    get_authenticator,
)
from strangeworks_core.platform.transport import StrangeworksTransport

ALLOWED_HEADERS = {""}


class Operation:
    """Object for definining requests made to the platform."""

    def __init__(
        self,
        query: str,
        allowed_vars: Optional[List[str]] = None,
        upload_files: bool = False,
    ) -> None:
        """Initialize object.

        Accepts a GraphQL query or mutation as a string. Derives variable names used by
        the query if none were provided.

        Parameters
        ----------
        query: str
            a GraphQL query or mutation as string.
        allowed_vars: Optional[List[str]]
            list to override which variables can be sent was part of query.
        """
        self.query = gql(query)
        self.allowed_vars = (
            allowed_vars
            if allowed_vars
            else list(
                map(
                    lambda x: x.variable.name.value,
                    self.query.definitions[0].variable_definitions,
                )
            )
        )
        self.upload_files = upload_files

    def variables(
        self, values: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Define which variables are available for this operation."""
        if not self.allowed_vars:
            return values

        vars = {}
        for k, v in values.items():
            if k in self.allowed_vars and v is not None:
                vars[k] = v
        return vars


class APIInfo(Enum):
    """Helper class/enum for identifying available API's from the platform."""

    SDK = {"api": "sdk", "auth_url": SDK_AUTH_URL}
    PLATFORM = {"api": "platform", "auth_url": SDK_AUTH_URL}
    PRODUCT = {"api": "products", "auth_url": PRODUCT_AUTH_URL}

    def get_auth_url(self) -> str:
        """Retrieve auth url for API.

        Return
        ------
        :str
            url endpoint for requesting auth tokens.
        """
        return self.value.get("auth_url")

    def get_api(self) -> str:
        """Retrieve API name.

        The name is used to construct the URL to access the API from the platform.
        Return
        ------
        :str
            API name.
        """
        return self.value.get("api")


class API:
    """Client for accessing various Strangeworks Platform API's."""

    def __init__(
        self,
        base_url: str,
        api_type: APIInfo,
        api_key: str = None,
        auth_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retries: int = 0,
    ) -> None:
        """Initialize platform API client.

        Provides access to the platform API methods to interact with the Strangeworks
        platform.

        Parameters
        ----------
        base_url: str
            The URL to send the GQL queries.
        api_key: Optional[str]
            Used to obtain and refresh authorization tokens.
        api_id : APIName
            Identifies which of the platform APIs to use.
        auth_token: Optional[str]
            jwt token used to authorize requests to the platform APIs.
        headers: Dict[str, str]
            Additional values to set in the header for the request. The header must
            belong to ALLOWED_HEADERS.
        """
        url = parse.urljoin(base_url, api_type.get_api())
        self.gql_client = Client(
            transport=StrangeworksTransport(
                url=url,
                api_key=api_key,
                authenticator=get_authenticator(
                    base_url=base_url, auth_url=api_type.get_auth_url()
                ),
                auth_token=auth_token,
                headers=headers,
                retries=retries,
                timeout=timeout,
            )
        )
        self.info: APIInfo = api_type

    def execute(self, op: Operation, **kvargs):
        """Execute an operation on the platform.

        Parameters
        ----------
        op: Operation
            which request to run
        variable_values; Optional[Dict[str, Any]]
            values to send with the request
        """
        try:
            result = self.gql_client.execute(
                document=op.query,
                variable_values=op.variables(kvargs),
                upload_files=op.upload_files,
            )
            return result
        except TransportQueryError as e:
            raise StrangeworksError(message="Error executing gql query") from e
        except Exception as ex:
            raise StrangeworksError(message="Error from product API") from ex
