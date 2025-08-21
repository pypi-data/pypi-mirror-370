"""config.py."""
import os
from typing import Optional

from strangeworks.core.config.base import ConfigSource
from strangeworks.core.config.defaults import DefaultConfig
from strangeworks.core.config.env import EnvConfig
from strangeworks.core.config.file import ConfigFile
from strangeworks.core.utils import fix_str_attr, is_empty_str

DEFAULT_CFG_FILE_PATH = "~/.config/strangeworks/sdk/cfg.toml"
DEFAULT_PROFILE_NAME = "default"


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
        super().__init__(**kwargs)
        self._cfg_sources = {"env": EnvConfig(), "default": DefaultConfig()}
        self._init_cfg_file()

    def _init_cfg_file(self) -> Optional[ConfigFile]:
        try:
            file = ConfigFile(
                file_path=os.path.expanduser(
                    os.getenv("STRANGEWORKS_CONFIG_PATH", DEFAULT_CFG_FILE_PATH)
                )
            )
            # config file may have an active profile set. if it is,
            # retrieve it and set it for everyone.
            _active_profile_from_file = file.get_active_profile()
            if _active_profile_from_file:
                self.set_active_profile(_active_profile_from_file)
            self._cfg_sources["file"] = file
        except FileNotFoundError:
            # ok if file doesn't exist.
            pass

    def get(self, key: str, profile: Optional[str] = None) -> Optional[str]:
        """Get configuration value.

        Checks sources in the order specified by _CFG_SOURCE_ORDER for requested item
        and returns as soon as a value is found.

        Parameters
        ----------
        key: str
            Name of the configuration variable
        profile: Optional[str]
            Name of the profile to use to retrieve value. Overrides active profile.

        Returns
        -------
        Optional[str]
            A string value corresponding to the key or None.
        """
        if "file" not in self._cfg_sources:
            self._init_cfg_file()

        # override active profile if caller provided one
        _profile = self._fix_profile(profile)
        for src_type in Config._CFG_SOURCE_ORDER:
            if src_type in self._cfg_sources:
                v = self._cfg_sources[src_type].get(key, _profile)
                if v:
                    return v
        return None

    def set(self, profile: Optional[str] = None, overwrite: bool = False, **params):
        """Set configuration variables.

        If a file configuration is missing, it will create one. Note that this method
        will not update the current active_profile to the profile provided for this
        call. In order to switch the active_profile, the set_active_profile method
        must be called explicitly.
        """
        fixed_profile = self._fix_profile(profile)

        for _, cfg in self._cfg_sources.items():
            cfg.set_active_profile(self.get_active_profile())
            cfg.set(profile=fixed_profile, overwrite=overwrite, **params)

        # try to create a config file if one doesn't exist. In the case that a file was
        # created after this object was initialized overwrite the file only if
        # overwrite is True.
        if "file" not in self._cfg_sources:
            cfg_file = ConfigFile.create_file(
                active_profile=self.get_active_profile(),
                file_path=os.path.expanduser(
                    os.getenv("STRANGEWORKS_CONFIG_PATH", DEFAULT_CFG_FILE_PATH)
                ),
                profile=fixed_profile,
                overwrite=overwrite,
                **params,
            )
            self._cfg_sources["file"] = cfg_file

    def set_active_profile(self, active_profile: str):
        """Update active profile.

        Update active profile for self and all ConfigSource objects contained in
        this object.That active profile for ConfigSource objects contained in this
        object will be updated only if its different than its current value.

        Parameters
        ----------
        active_profile: str
            The profile to use as default profile.

        Returns
        -------
        None
        """
        super().set_active_profile(active_profile)
        for _, cfg in self._cfg_sources.items():
            if cfg.get_active_profile() != self.get_active_profile():
                cfg.set_active_profile(self.get_active_profile())

    def _fix_profile(self, profile: Optional[str] = None) -> str:
        """Return fixed profile.

        Converts given profile value by removing leading and trailing spaces and
        converting it to lowercase.
        Returns active profile if none or empty string was passed in.

        Parameters
        ----------
        profile: Optional[str] = None
            Name of the profile. Defaults to None

        Returns
        -------
        :str
            profile name adjusted as described above.
        """
        return (
            self.get_active_profile()
            if is_empty_str(profile)
            else fix_str_attr(profile)
        )
