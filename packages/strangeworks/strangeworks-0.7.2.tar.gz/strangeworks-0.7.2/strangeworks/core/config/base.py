"""base.py."""
from abc import ABC, abstractmethod
from typing import Optional

from strangeworks.core.utils import fix_str_attr, is_empty_str

DEFAULT_PROFILE_NAME = "default"


class ConfigSource(ABC):
    """Base class for configuration source classes.

    Methods
    -------
    get(key: str, profile: Optional[str])
        retrieves the value for the given configuration parameter. If profile is
        specified, it overrides active profile.
    set(profile: str, overwrite: bool, **params)
        updates existing configuration with the key-value pairs from `**params`.
        If profile is specified, it overrides active profile.
    set_active_profile(active_profile: str)
        set active profile name
    get_active_profile()-> str:
        retrieve the active profile name.
    """

    def __init__(self, active_profile: str = DEFAULT_PROFILE_NAME, **kwargs):
        """Create a ConfigSource object."""
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

    @abstractmethod
    def get(self, key: str, profile: Optional[str]) -> Optional[str]:
        pass

    @abstractmethod
    def set(self, profile: str, overwrite: bool = False, **params):
        pass
