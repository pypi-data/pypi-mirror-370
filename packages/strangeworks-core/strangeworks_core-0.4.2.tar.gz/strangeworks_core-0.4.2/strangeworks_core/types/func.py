"""func.py."""
from dataclasses import dataclass
from typing import Any, Callable, Optional, ParamSpec, Tuple, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

# using dataclass instead of pydantic as the latter has limitations with validating
# Callable types.


@dataclass
class Func:
    """
    Func represents a function to be executed as a batch job.

    Attributes
    ----------
    func : Callable[..., Any]
        The function to be executed.
    fargs : Tuple[Any]
        The function's arguments.
    fkwargs : dict[str, Any]
        The function's keyword arguments.
    requirements_path : Optional[str]
        A path to the function's requirements file.
    """

    func: Callable[P, T]
    fargs: Tuple[Any]
    fkwargs: dict[str, Any]
    requirements_path: Optional[str] = None
