"""utils.py."""

from datetime import datetime
from typing import Optional


def is_empty_str(s: str) -> bool:
    """Check if string is empty.

    A string is considered to be empty if any one of the following conditions are true:
        - it is set to `None` or
        - consists exclusively of spaces
     - is equal to `""`
    """
    return not s or s == "" or s.isspace()


def str_to_datetime(s: Optional[str]) -> Optional[datetime]:
    return (
        None if is_empty_str(s) else datetime.strptime(s.strip(), "%Y-%m-%dT%H:%M:%S%z")
    )
