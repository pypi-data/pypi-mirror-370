"""credentials.py."""

from pydantic import BaseModel

from strangeworks_core.config.defaults import DEFAULT_URL


class Credentials(BaseModel):
    """Credentials for Strangeworks SDK users and Products."""

    api_key: str
    host_url: str = DEFAULT_URL
