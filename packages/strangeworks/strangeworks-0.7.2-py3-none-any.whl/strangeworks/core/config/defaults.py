"""defaults.py."""
from typing import Optional

from strangeworks.core.config.base import DEFAULT_PROFILE_NAME, ConfigSource

DEFAULT_URL = "https://api.strangeworks.com"


class DefaultConfig(ConfigSource):
    """Configuration Source for default values."""

    cfg = {"url": DEFAULT_URL}

    def get(self, key: str, profile: str = DEFAULT_PROFILE_NAME) -> Optional[str]:
        """Strangeworks SDK Default Configurations.

        Serves as a source of default config values.  Any request for a profile other
        than default will return None.
        """
        if profile != DEFAULT_PROFILE_NAME or key not in DefaultConfig.cfg:
            return None

        return DefaultConfig.cfg.get(key)

    def set(
        self, profile: str = DEFAULT_PROFILE_NAME, overwrite: bool = False, **params
    ):
        """Set (no-op) for default profile."""
        return
