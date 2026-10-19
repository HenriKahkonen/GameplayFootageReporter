from utils.errors import MalformedSettingsError
from copy import deepcopy
from typing import Any, Optional
import settings

class Settings:
    def __init__(self):
        """
        Loader for settings.py. Copies the values into instance attributes so
        they can be changed during runtime without touching the settings module.
 
        Raises MalformedSettingsError if any value from settings.py is None.
        Values loaded from the .env file are allowed to be None.
        """
 
        # --- Output options ---
        try:
            self.OUTPUT_TO_CUSTOM_DIRECTORY: bool = settings.OUTPUT_TO_CUSTOM_DIRECTORY
            self.LOG_OUTPUT: bool = settings.LOG_OUTPUT
    
            self.CSV_OUTPUT: bool = settings.CSV_OUTPUT
            self.CSV_SEPARATOR: str = settings.CSV_SEPARATOR
            self.CSV_FLOATS_WITH_COMMA: bool = settings.CSV_FLOATS_WITH_COMMA
    
            self.SQLITE_OUTPUT: bool = settings.SQLITE_OUTPUT
    
            # --- Video and ignored files ---
            self.SUPPORTED_VIDEO_FILETYPES: list[str] = deepcopy(settings.SUPPORTED_VIDEO_FILETYPES)
            self.IGNORED_FILETYPES: list[str] = deepcopy(settings.IGNORED_FILETYPES)
    
            # --- Naming conventions ---
            self.PLATFORM_IN_FOLDERNAME: bool = settings.PLATFORM_IN_FOLDERNAME
            self.DEFAULT_PLATFORM: str = settings.DEFAULT_PLATFORM
            self.PLATFORM_PREFIX_SEPARATOR: str = settings.PLATFORM_PREFIX_SEPARATOR
            self.RELEASE_YEAR_IN_FOLDERNAME: bool = settings.RELEASE_YEAR_IN_FOLDERNAME
    
            self.GAME_PLATFORMS: dict[str, str] = deepcopy(settings.GAME_PLATFORMS)
            self.FOOTAGE_CATEGORIES: dict[str, tuple[str, str]] = deepcopy(settings.FOOTAGE_CATEGORIES)
    
            # --- Obsidian ---
            self.SCAN_OBSIDIAN_DB: bool = settings.SCAN_OBSIDIAN_DB
            self.OBSIDIAN_HEADERS: dict[str, Any] = deepcopy(settings.OBSIDIAN_HEADERS)

            self.OBSIDIAN_RATING_MIN : int = settings.OBSIDIAN_RATING_MIN
            self.OBSIDIAN_RATING_MAX : int = settings.OBSIDIAN_RATING_MAX
            self.OBSIDIAN_RATING_USE_STAR_SYSTEM : bool = settings.OBSIDIAN_RATING_USE_STAR_SYSTEM
    
            # --- Loaded from .env (allowed to be None) ---
            self.GAMEPLAY_FOOTAGE_PATH: Optional[str] = settings.GAMEPLAY_FOOTAGE_PATH
            self.OBSIDIAN_DB_PATH: Optional[str] = settings.OBSIDIAN_DB_PATH
            self.CUSTOM_OUTPUT_PATH: Optional[str] = settings.CUSTOM_OUTPUT_PATH
    
            self.validate()
        except AttributeError as e:
            msg = (f"It looks like your settings.py file is malformed. Loading settings returned error: \n{e}")
            raise MalformedSettingsError(msg)
 
    # Settings that come from the .env file and may legitimately be None
    _ENV_SETTINGS = frozenset({
        "GAMEPLAY_FOOTAGE_PATH",
        "OBSIDIAN_DB_PATH",
        "CUSTOM_OUTPUT_PATH",
    })

    def validate(self) -> None:
        """
        Checks the current setting values. Can also be called again after
        changing values at runtime.
 
        Raises:
            MalformedSettingsError: if a non-.env setting is None, or if
                settings contradict each other.
        """
 
        # 1. No None values, except for the ones loaded from .env
        missing = [
            name
            for name, value in vars(self).items()
            if name.isupper() and name not in self._ENV_SETTINGS and value is None
        ]
        if missing:
            raise MalformedSettingsError(
                f"The following settings in settings.py are None: {', '.join(missing)}"
            )
 
        # 2. Settings that contradict each other
        if self.CSV_FLOATS_WITH_COMMA and self.CSV_SEPARATOR == ",":
            raise MalformedSettingsError(
                'CSV_SEPARATOR cannot be "," when CSV_FLOATS_WITH_COMMA is True.'
            )
 
        # 3. Settings that are conditionally required in .env
        if self.OUTPUT_TO_CUSTOM_DIRECTORY and not self.CUSTOM_OUTPUT_PATH:
            raise MalformedSettingsError(
                "OUTPUT_TO_CUSTOM_DIRECTORY is True, but CUSTOM_OUTPUT_PATH is not set in .env."
            )
        if self.SCAN_OBSIDIAN_DB and not self.OBSIDIAN_DB_PATH:
            raise MalformedSettingsError(
                "SCAN_OBSIDIAN_DB is True, but OBSIDIAN_DB_PATH is not set in .env."
            )
 
        # 4. Light type checks on the collections
        if not all(ext.startswith(".") for ext in self.SUPPORTED_VIDEO_FILETYPES):
            raise MalformedSettingsError(
                'Every entry in SUPPORTED_VIDEO_FILETYPES must start with a dot, e.g. ".mp4".'
            )

