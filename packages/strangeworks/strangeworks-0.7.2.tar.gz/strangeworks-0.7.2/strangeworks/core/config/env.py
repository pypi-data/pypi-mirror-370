"""env.py."""

from strangeworks_core.config.env import EnvConfig as BaseEnvConfig

from strangeworks.core.config.base import DEFAULT_PROFILE_NAME
from strangeworks.core.utils import fix_str_attr, is_empty_str


class EnvConfig(BaseEnvConfig):
    """Obtain configuration from environment variables.

    Environment variables are expected to be in the following format:
        STRANGEWORKS_CONFIG_{profile}_{key}
    where `profile` and `key` are non-empty strings in uppercase
    letters.
    """

    def __init__(self, active_profile: str = DEFAULT_PROFILE_NAME, **kwargs):
        """Create a ConfigSource object."""
        super().__init__(**kwargs)
        self._active_profile = active_profile

    def set_active_profile(self, active_profile: str):
        """Set active profile value.

        Calling this method with active profile set to  a None value or empty string or
        spaces is a no-op.
        """
        if not is_empty_str(active_profile):
            self._active_profile = fix_str_attr(active_profile)

    def get_active_profile(self, **kwargs) -> str:
        """Retrieve active profile value."""
        return self._active_profile
