"""file.py."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import AliasChoices, BaseModel, Field


class File(BaseModel):
    """Class that represents a file.

    Attributes
    ----------
    slug: str
        User-friendly identifier.
    file_id: Optional[str]
        Internal identifier.
    label: Optional[str]
        Label
    file_name: Optional[str]
        File name used when saving on platform.
    url: Optional[str]
        URL to access the file from the platform.
    date_created: Optional[datetime]
        Date when the file object was created on platform.
    date_updated: Optional[datetime]
        Date when the file object was last updated.
    """

    slug: str
    file_id: Optional[str] = Field(default=None, alias=AliasChoices("id", "file_id"))
    label: Optional[str] = None
    file_name: Optional[str] = Field(
        default=None, alias=AliasChoices("file_name", "fileName")
    )
    url: Optional[str] = None
    file_size_bytes: Optional[int] = Field(
        default=None, alias=AliasChoices("metaSizeBytes", "file_size_bytes")
    )
    date_created: Optional[datetime] = Field(
        default=None, alias=AliasChoices("date_created", "dateCreated")
    )
    date_updated: Optional[datetime] = Field(
        default=None, alias=AliasChoices("date_updated", "dateUpdated")
    )

    @classmethod
    def from_dict(cls, res: Dict[str, Any]) -> "File":
        """Create a File object from a Dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for File.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        res : Dict[str, Any]
            File represented as a dictionary.
        """
        return cls(**res)
