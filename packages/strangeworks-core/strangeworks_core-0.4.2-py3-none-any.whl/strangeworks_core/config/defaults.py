"""defaults.py."""
from typing import Optional

from strangeworks_core.config import DEFAULT_PROFILE_NAME
from strangeworks_core.config.base import ConfigSource

DEFAULT_URL = "https://api.strangeworks.com"


class DefaultConfig(ConfigSource):
    """Configuration Source for default values"""

    cfg = {"url": DEFAULT_URL}

    def __init__(self) -> None:
        pass

    def get(self, key: str, profile: str = DEFAULT_PROFILE_NAME) -> Optional[str]:
        """Strangeworks SDK Default Configurations

        Serves as a source of default config values.  Any request for a profile other
        than default will return None.
        """
        if profile != DEFAULT_PROFILE_NAME or key not in DefaultConfig.cfg:
            return None

        return DefaultConfig.cfg[key]

    def set(
        self, profile: str = DEFAULT_PROFILE_NAME, overwrite: bool = False, **params
    ):
        """
        setting parameters is a no-op for defaults.
        """
        pass
