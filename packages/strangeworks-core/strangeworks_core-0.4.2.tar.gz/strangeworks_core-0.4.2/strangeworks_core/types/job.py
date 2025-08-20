"""jobs.py."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from deprecated import deprecated
from pydantic import AliasChoices, BaseModel, Field

from strangeworks_core.types.base import RemoteObject
from strangeworks_core.types.file import File
from strangeworks_core.types.resource import Resource


class Status(str, Enum):
    """Enumeration of possible job statuses."""

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal_state(self):
        """Check if status is corresponds to a terminal state.

        Returns
        -------
        return True if self is in [Status.CANCELLED, Status.COMPLETED, Status.FAILED],
        False otherwise.
        """
        return self in [Status.CANCELLED, Status.COMPLETED, Status.FAILED]


class JobFile(BaseModel):
    """Object which represents a Strangeworks platform job file entry.

    Attributes
    ----------
    file: File
    sort_weight: Optional[int]
        Sort weight of the file.
    is_public: Optional[bool]
        Indicates whether the file is public.
    """

    file: File
    sort_weight: Optional[int] = Field(
        default=None, alias=AliasChoices("sort_weight", "sortWeight")
    )
    is_public: Optional[bool] = Field(
        default=None, alias=AliasChoices("is_public", "isPublic")
    )

    @classmethod
    def from_dict(cls, res: Dict[str, Any]) -> "JobFile":
        """Generate a JobFile object from dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for JobFile.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        res: Dict[str, Any]
            JobFile attribues represented as a dictionary.

        Return
        ------
        "JobFile"
            a job file object.
        """
        return cls(**res)


class Job(RemoteObject):
    """Object representing a Strangeworks platform job entry.

    Attributes
    ----------
    slug: str
        User-friendly identifier.
    job_id: Optional[str]
        Internal identifier.
    external_identifier: Optional[str]
        Identifier if the execution of the job is occurring on an external
        platform.
    status: Optional[Status]
        Status of the job.
    is_terminal_state: Optional[bool]
        Indicates whether the current state of the job is terminal meaning
        no further state changes will occur.
    remote_status: Optional[str]
        Status of the job on external platform. Inherited.
    job_data: Optional[str]
        Attributes related to the job execution.
    job_data_schema: Optional[str]
        JSON schema to which the data is expected to adhere to.
    date_created: Optional[datetime]
        Date when the job object was created on platform.
    date_updated: Optional[datetime]
        Date when the job object was last updated.
    resource: Optional[Resource]
        Resource associated with the job.
    child_jobs: Optional[List[Job]]
        List of jobs which were spawned by the job.
    files: Optional[List[JobFile]]
        List of files associated with the job.
    tags: Optional[List[str]]
        List of tags associated with the job.
    """

    def __init__(self, *args, **kwargs):
        """Initialize Job Object."""
        super().__init__(*args, **kwargs)
        self.remote_id = self.external_identifier

    slug: str
    job_id: Optional[str] = Field(default=None, alias=AliasChoices("id", "job_id"))
    external_identifier: Optional[str] = Field(
        default=None,
        alias=AliasChoices(
            "external_identifier",
            "externalIdentifier",
        ),
        serialization_alias="externalIdentifier",
    )
    status: Optional[Status] = Field(default=None)
    is_platform_terminal_state: Optional[bool] = Field(
        default=None,
        alias=AliasChoices("is_terminal_state", "isTerminalState"),
        serialization_alias="isTerminalState",
    )
    job_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias=AliasChoices("job_data", "jobData", "data"),
        serialization_alias="jobData",
    )
    job_data_schema: Optional[str] = Field(
        default=None,
        alias=AliasChoices("job_data_schema", "jobDataSchema", "dataSchema"),
    )
    date_created: Optional[datetime] = Field(
        default=None, alias=AliasChoices("date_created", "dateCreated")
    )
    date_updated: Optional[datetime] = Field(
        default=None, alias=AliasChoices("date_updated", "dateUpdated")
    )
    resource: Optional[Resource] = None
    child_jobs: Optional[List["Job"]] = Field(
        default=None, alias=AliasChoices("childJobs", "child_jobs")
    )
    files: Optional[List[JobFile]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)

    @classmethod
    def from_dict(cls, res: Dict[str, Any]) -> "Job":
        """Generate a Job object from dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Job.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        res: Dict[str, Any]
            Job attribues represented as a dictionary.

        Return
        ------
        "Job"
            a job object.
        """
        return cls(**res)

    @deprecated(
        reason=(
            "This method is deprecated and will be removed. Use is_terminal_state instead."  # noqa E501
        )
    )
    def is_complete(self) -> bool:
        """Check if job is in terminal state.

        deprecated method, kept to limit number of changes
        required for extension SDKs
        """
        return self.is_platform_terminal_state

    @property
    def is_terminal_state(self) -> bool:
        """Return if job is in terminal state.

        If _is_terminal_state was set, return that value. Otherwise, return
        self.status.is_terminal_state
        """
        return (
            self.is_platform_terminal_state
            if self.is_platform_terminal_state is not None
            else self.status.is_terminal_state
        )

    def get_sw_status(self):
        """Return status.

        This is the Strangeworks platform definition of job status.
        """
        return self.status
