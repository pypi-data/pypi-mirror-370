"""config.py."""
import os
from typing import Optional

from strangeworks_core.config import DEFAULT_PROFILE_NAME
from strangeworks_core.config.base import ConfigSource
from strangeworks_core.config.defaults import DefaultConfig
from strangeworks_core.config.env import EnvConfig
from strangeworks_core.config.file import ConfigFile
from strangeworks_core.utils import is_empty_str

DEFAULT_CFG_FILE_PATH = "~/.config/strangeworks/sdk/cfg.toml"


class Config(ConfigSource):
    """Main configuration for the SDK.

    Uses multiple sources to retrieve and save values. The hierarchy of the
    sources is specified by the _CFG_SOURCE_ORDER list.
    """

    _CFG_SOURCE_ORDER = ["env", "file", "default"]

    def __init__(self, **kwargs) -> None:
        """Initialize  object.

        Initialize with various configuration sources (environment, defaults, and file
        if file exists)

        User can specify a custom path for a configuration file by setting the
        STRANGEWORKS_CONFIG_PATH environment variable.
        """
        self._cfg_sources = {"env": EnvConfig(**kwargs), "default": DefaultConfig()}
        self._init_cfg_file()

    def _init_cfg_file(self) -> Optional[ConfigFile]:
        try:
            file = ConfigFile(
                file_path=os.path.expanduser(
                    os.getenv("STRANGEWORKS_CONFIG_PATH", DEFAULT_CFG_FILE_PATH)
                )
            )
            self._cfg_sources["file"] = file
        except FileNotFoundError:
            # ok if file doesn't exist.
            pass

    def get(self, key: str, profile: Optional[str] = None, **kvargs) -> Optional[str]:
        """Get configuration value.

        Checks sources in the order specified by _CFG_SOURCE_ORDER for requested item
        and returns as soon as a value is found.
        """
        if "file" not in self._cfg_sources:
            self._init_cfg_file()

        _prof = self._fix_profile(profile)
        for src_type in Config._CFG_SOURCE_ORDER:
            if src_type in self._cfg_sources:
                v = self._cfg_sources[src_type].get(key=key, profile=_prof, **kvargs)
                if v:
                    return v
        return None

    def set(self, profile: str, overwrite: bool = False, **params):
        """Set configuration variables.

        If a file configuration is missing, it will create one.
        """
        fixed_profile = self._fix_profile(profile)
        for _, cfg in self._cfg_sources.items():
            cfg.set(profile=fixed_profile, overwrite=overwrite, **params)

        # try to create a config file if one doesn't exist. In the case that a file was
        # created after this object was initialized overwrite the file only if
        # overwrite is True.
        if "file" not in self._cfg_sources:
            cfg_file = ConfigFile.create_file(
                file_path=os.path.expanduser(
                    os.getenv("STRANGEWORKS_CONFIG_PATH", DEFAULT_CFG_FILE_PATH)
                ),
                profile=fixed_profile,
                overwrite=overwrite,
                **params,
            )
            self._cfg_sources["file"] = cfg_file

    def _fix_profile(self, profile: Optional[str] = None) -> str:
        """Return default profile name if given profile is an empty string."""
        return (
            DEFAULT_PROFILE_NAME if is_empty_str(profile) else profile.strip().lower()
        )
