"""batch.py."""
from pydantic import BaseModel


class Options(BaseModel):
    """
    Options is a dataclass that represents options for a batch job.

    Attributes
    ----------
    max_retries : int
        The maximum number of times to retry a batch job.
        Retries only happen if the batch job fail.
        Default set to no retries.
    max_duration : int
        The maximum duration of a batch job in seconds.
        Before the job is marked as failed.
        Default set to seven days.
    """

    max_retries: int = 0
    max_duration: int = 604800
