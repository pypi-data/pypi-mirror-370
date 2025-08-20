"""base.py."""

from abc import ABC, abstractmethod
from typing import Optional


class ConfigSource(ABC):
    """Base class for configuration source classes.

    Methods
    -------
    get(key: str, profile: Optional[str])
        retrieves the value for the given configuration parameter
    set(profile: str, overwrite: bool, **params)
        updates existing configuration with the key-value pairs from `**params`.
    """

    @abstractmethod
    def get(self, key: str, profile: Optional[str] = None, **kwargs) -> Optional[str]:
        pass

    def get_bool(self, key: str, profile: Optional[str] = None, **kwargs) -> bool:
        """Get Boolean configuration value.

        Parameters
        ----------
        key: str
            variable name.
        profile: Optional[str] = None
            Profile name to use in retrieving the value. Optional.

        Returns
        -------
        : bool
            True if value lowercase is "true", "t", or "1", False otherwise
        """
        _val: str = self.get(key=key, profile=profile)
        return False if _val is None else _val.strip().lower() in ["true", "t", "1"]

    @abstractmethod
    def set(self, profile: str = "default", overwrite: bool = False, **params):
        pass
