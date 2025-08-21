"""file.py."""
import os
from typing import Optional

import tomlkit
from tomlkit.exceptions import NonExistentKey

from strangeworks.core.config.base import DEFAULT_PROFILE_NAME, ConfigSource
from strangeworks.core.errors.error import StrangeworksError
from strangeworks.core.utils import fix_str_attr, is_empty_str

DEFAULT_CFG_FILE_PATH = "~/.config/strangeworks/sdk/cfg.toml"


class ConfigFile(ConfigSource):
    """Read/Write configuration to a file.

    Provides functionality to store and retrieve key-value pairs from a file. The
    file contents should be in TOML format. All table and key names are expected to
    be in lowercase letters. Each table represents a separate configuration profile.

    ConfigFile will retrieve the latest values in the file even if the file was
    modified externally after the object was initialized.

    Attributes
    ----------
    _file_path: Optional[str]
        Path to the file. Can use Using (~) or (~user) as shorthand for
        user's home directory.
    _cfg: TOMLDocument
        object that contains configuration values.
    _stat: stat_result
        object that contains information about the config file. Set each time
        configuration is read in.

    """

    def __init__(self, file_path: Optional[str] = None):
        """Initialize object.

        Parameters
        ----------
        file_path: str
            path to the configuration file.

        Raises
        ------
        FileNotFoundException
            If file does not exist.
        """
        if is_empty_str(file_path):
            raise StrangeworksError.invalid_argument(
                message="File path cannot be None or empty string."
            )

        self._file_path = os.path.expanduser(file_path)
        # call base class init first, then set the active_profile in _load method.
        super().__init__()
        self._load()

    def _load(self):
        """Load configuration from file."""
        with open(self._file_path, "rb") as f:
            self._cfg = tomlkit.load(f)
            self._stat = os.stat(self._file_path)
            active_profile = self._cfg.get("active_profile") or DEFAULT_PROFILE_NAME
            self.set_active_profile(active_profile)
            f.close()

    def _reload(self):
        """Check last modified time of file and reload if it has changed."""
        try:
            last_modified = os.path.getmtime(self._file_path)
            if last_modified > self._stat.st_mtime:
                self._load()
        except FileNotFoundError:
            # file has been removed since startup...go with what we have
            pass

    def get(self, key: str, profile: Optional[str] = None) -> Optional[str]:
        """
        Retrieve value of given key.

        If the source configuration file has a modification timestamp that is
        more recent than when configuration was read in, configuration will be
        reloaded from the file before it is retrieved.

        Parameters
        ----------
        key:str
            Name of the configuration variable
        profile: Optional[str]
            Name of the profile to use for the value.

        Returns
        -------
        Value of the requested configuration or None
        """
        self._reload()
        _profile = fix_str_attr(profile) or self.get_active_profile()
        if is_empty_str(key) or is_empty_str(_profile):
            return None

        _key = fix_str_attr(key)
        try:
            p = self._cfg.item(_profile)
            val = p[_key]
            return val
        except NonExistentKey:
            return None

    def set(
        self,
        profile: str,
        overwrite: bool = False,
        **params,
    ):
        """Set configuration values and save to file.

        If a key already exists, its value will be overwritten only if `overwrite` is
        set to True.

        Parameters
        ----------
        profile: str
            Name of the profile to use for the setting values. Must be a non-empty
            string.
        overwrite: bool
            Indicates whether a value that already exists should be overwritten
        **params:
            key-value pairs denoting configuration values.
        """
        if is_empty_str(profile):
            raise StrangeworksError.invalid_argument(
                "Profile name cannot be an empty string or None."
            )
        self._reload()
        _profile = fix_str_attr(profile)
        if _profile not in self._cfg:
            self._cfg[_profile] = tomlkit.table()
        for key, val in params.items():
            _key = fix_str_attr(key)
            if _key not in self._cfg[_profile] or overwrite:
                self._cfg[_profile][_key] = val
        self._cfg["active_profile"] = self.get_active_profile()
        ConfigFile._write_file(self._cfg.as_string(), self._file_path)

    @staticmethod
    def create_file(
        profile: str,
        active_profile: Optional[str] = None,
        file_path: Optional[str] = None,
        overwrite: bool = False,
        **params,
    ):
        """Create configuration file."""
        if is_empty_str(file_path):
            raise StrangeworksError.invalid_argument(
                message="File path cannot be None or empty string."
            )
        if os.path.exists(file_path) and not overwrite:
            raise StrangeworksError.invalid_argument(
                message="File {fpath} already exists. If you are ok with the existing"
                "file being overwritten, call this method with overwrite=True"
            )
        if is_empty_str(profile):
            raise StrangeworksError.invalid_argument(
                "Profile cannot be an empty string or None"
            )

        fpath = os.path.expanduser(file_path)
        _profile = fix_str_attr(profile)
        doc = tomlkit.document()
        doc.add("title", "Strangeworks SDK configuration settings.")
        doc.add("active_profile", active_profile or DEFAULT_PROFILE_NAME)
        t = tomlkit.table()
        for key, value in params.items():
            _key = fix_str_attr(key)
            t.add(_key, value)
        doc.add(_profile, t)

        ConfigFile._write_file(cfg_str=doc.as_string(), file_path=fpath)
        return ConfigFile(file_path=fpath)

    @staticmethod
    def _write_file(cfg_str: str, file_path: Optional[str]):
        if is_empty_str(file_path):
            raise StrangeworksError.invalid_argument(
                message="File path cannot be None or empty string."
            )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(cfg_str)
            f.close()
