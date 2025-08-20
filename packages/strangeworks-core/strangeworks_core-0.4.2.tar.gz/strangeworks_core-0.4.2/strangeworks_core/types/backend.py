"""backends.py."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import AliasChoices, Field

from strangeworks_core.types.base import RemoteObject
from strangeworks_core.types.product import Product
from strangeworks_core.utils import is_empty_str


class Status(Enum):
    """Enumeration of possible backend statuses."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def from_str(s: Optional[str] = None) -> Status:
        """Return Status from string."""
        if is_empty_str(s):
            return Status.UNKNOWN
        adj_str = s.strip().upper()
        possible_status = [e for e in Status if e.value == adj_str]
        return possible_status[0] if len(possible_status) == 1 else Status.UNKNOWN

    def __str__(self):
        return str(self.value)


class Backend(RemoteObject):
    """Represents a Strangeworks platform Backend object.

    Parameters
    ----------
    name: str
        Backend name.
    slug: str
        User-friendly identifier.
    status: Status
        Status of the backend.
    backend_id:  Optional[str]
        Internal identifier.
    data: Optional[Dict[str,Any]]
        Typically configuration data.
    data_schema: Optional[str]
        JSON schema to which the data is expected to adhere to.
    remote_backend_id: Optional[str]
        Identifier used by the vendor.
    remote_status: Optional[str]
        Status from the vendor. Inherited.
    date_created: Optional[datetime]
        Date when the backend object was created on platform.
    date_updated: Optional[datetime]
        Date when the backend object was last updated.
    product: Optional[Product]
        Product associated with the backend represended as a dictionary.
    """

    name: str
    slug: str
    status: Status
    backend_id: Optional[str] = Field(
        default=None, alias=AliasChoices("id", "backend_id")
    )
    data: Optional[Dict[str, Any]] = Field(default=None)
    data_schema: Optional[str] = Field(
        default=None, alias=AliasChoices("data_schema", "dataSchema")
    )
    remote_backend_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("remote_backend_id", "remoteBackendId"),
        serialization_alias="remoteBackendID",
    )
    date_created: Optional[str] = Field(
        default=None, alias=AliasChoices("date_created", "dateCreated")
    )
    date_updated: Optional[str] = Field(
        default=None, alias=AliasChoices("date_updated", "dateUpdated")
    )
    product: Optional[Product] = None

    def __init__(self, *args, **kwargs):
        """Initialize Backend object."""
        super().__init__(*args, **kwargs)
        self.remote_id = self.remote_backend_id

    @classmethod
    def from_dict(cls, backend: Dict[str, Any]) -> Backend:
        """Create a Backend object from Dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Backend.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        d : Dict[str, Any]
            Backend represented as a dictionary.
        """
        return cls(**backend)

    @property
    def remote_id(self) -> str:
        """Return remote backend id."""
        return self.remote_backend_id

    def get_sw_status(self):
        """Return Strangeworks status."""
        return self.status
