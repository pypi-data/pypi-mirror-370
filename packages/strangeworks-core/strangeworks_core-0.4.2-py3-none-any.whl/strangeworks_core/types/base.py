"""remote.py."""
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field


class RemoteObject(BaseModel, ABC):
    """Class that represents a remote object.

    Attributes
    ----------
    remote_id: Optional[str]
        id used to retrieve information about object from remote source.
    remote_status: Optional[str]
        Status of the job on external platform.
    """

    remote_id: Optional[str] = Field(default=None)
    remote_status: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "remote_status",
            "remoteStatus",
        ),
        serialization_alias="remoteStatus",
    )

    @abstractmethod
    def get_sw_status(self):
        """Return Strangeworks Status."""
        ...
