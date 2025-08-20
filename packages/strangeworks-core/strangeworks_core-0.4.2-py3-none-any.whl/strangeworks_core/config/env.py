"""env.py."""

import os
from typing import Optional

from strangeworks_core.config.base import ConfigSource
from strangeworks_core.config.defaults import DEFAULT_PROFILE_NAME
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.utils import is_empty_str

_DEFAULT_NAMESPACE = "STRANGEWORKS_CONFIG"
_CUSTOM_NS_ENVVAR_NAME = "_SW_CONFIG_INTERNAL_ENVVAR_NAMESPACE"
_USE_NS_ENVVAR_NAME = "_SW_CONFIG_INTERNAL_ENVVAR_USE_NAMESPACE"


class EnvConfig(ConfigSource):
    """Obtain configuration from environment variables.

    Environment variable names must be in uppercase.

    This class defaults to using a simple namespacing mechanism in order to prevent
    clashing of commonly used variable names. When namespacing is enabled, EnvConfig
    only deals with environment variables to be specified in the following format:
        {NAMESPACE}_{PROFILE}_{VARIABLE_NAME}

    The default prefix is STRANGEWORKS_CONFIG and the default profile name is 'default'
    All variables under the default profile using the default namespace are expected
    to be in the format:
        STRANGEWORKS_CONFIG_DEFAULT_{VARIABLE_NAME}

    Users can specify their own custom namespace. For example a default username for
    MYSQL and MongoDB can be stored with two different custom namespaces as follows:
        MYSQL_DEFAULT_USERNAME
        MONGODB_DEFAULT_USERNAME

    If namespaces are disabled, each lookup is the equivalent of calling os.getenv with
    the variable name as uppercase. Profiles are also disabled/ignored if namespaces is
    disabled.
    """

    def __init__(
        self, use_namespace: bool = True, namespace: str = _DEFAULT_NAMESPACE, **kwargs
    ):
        """Initialize EnvConfig object.

        Parameters
        ----------
        use_namespace: bool
            if true, lookups will try to retrieve the given key without prepending a
            prefix or profile. Defaults to False.
        namespace: str
            Allows caller to specify a custom prefix.
        """

        if use_namespace and is_empty_str(namespace):
            raise StrangeworksError(
                "Empty namespace is not allowed if use_namespaces is set to True."
            )
        self.namespace = namespace.upper() if use_namespace else None

    def get(
        self,
        key: str,
        profile: str = DEFAULT_PROFILE_NAME,
        ignore_namespace: bool = False,
        namespace: Optional[str] = None,
    ) -> Optional[str]:
        """Retrieve the values from environment variables.

        The method will convert all lowercase key/profile values to uppercase.

        The method will convert all lowercase key or profile values to uppercase. It
        will also replace hyphens (-) with underscores (_) as dashes are not allowed in
        environment variables.

        Parameters
        ----------
        key: str
            variable name.
        profile: str
            Profile name to use in retrieving the value. Defaults to "default"
        ignore_namespace: bool
            Do not use namespace for this lookup if True. Defaults to False.
        namespace: Optional[str]
            Namespace to use for this lookup.
        """
        if is_empty_str(key):
            return None

        env_var = self.get_envvar_name(
            key=key,
            profile=profile,
            namespace=None if ignore_namespace else namespace or self.namespace,
        )
        return os.getenv(env_var)

    def set(
        self,
        profile: str = DEFAULT_PROFILE_NAME,
        overwrite: bool = False,
        ignore_namespace: bool = False,
        namespace: Optional[str] = None,
        **params,
    ):
        """Set method for environment variables.

        Existing environment variables will be updated only if overwrite is set
        to True.
        """
        for key, val in params.items():
            envvar_name = self.get_envvar_name(
                key=key,
                profile=profile,
                namespace=None if ignore_namespace else namespace or self.namespace,
            )
            # overwrite existing envvars only if overwrite is True.
            if envvar_name not in os.environ or overwrite:
                os.environ[envvar_name] = val

    def get_envvar_name(
        self,
        key: str,
        profile: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> str:
        """Construct environment variable name from key, profile, namespace settings.

        The constructed environment variable name will be of the format:
            {namespace}_{profile}_{key}

        if namespace and profile are not None or
            {namespace}__{key}

        if profile is None or
            {key} if namespace and profile are None

        All hypthens in key, profile, and namespace will be replaced with
        underscores because POSIX says so :-)

        Parameters
        ----------
        key: str
            the key name.
        profile: Optional[str]
            used as a container to group related keys together. Defaults to None.
        namespace: Optional[str]
            typically used to distinguish strangeworks configs from everyone else.
            Defaults to None.

        Returns
        -------
        : str
            the environment variable name
        """
        _key = key.replace("-", "_").upper()
        _ns = namespace.replace("-", "_").upper() if namespace else namespace
        _profile = profile.replace("-", "_").upper() if profile else profile
        return (
            _key
            if not namespace
            else (f"{_ns}_{_profile}_{_key}" if profile else f"{_ns}__{_key}")
        )
