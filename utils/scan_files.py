"""
Module for scanning files and folders to analyze them.
"""
import os
import re
from pathlib import Path
from utils.settings_loader import Settings
from utils.parse_obsidian_notes import parse_obsidian_note
from utils.errors import (
    TooHighRatingError,
    TooLowRatingError,
    CannotParseRatingError,
    InvalidStarRatingError
    )

def get_footage_folders(directory:str | Path) -> list[str]:
    """Get the list of folders inside the root path in alphabetical order. 
    Does not return absolute paths, only the folder names."""
    return sorted(
        item for item in os.listdir(directory)
        if os.path.isdir(os.path.join(directory,item))
        )


def parse_release_year_from_folder_name(
        folder_name:str | Path,
        settings: Settings
        ) -> tuple[int | None, str]:
    """
    Takes the folder name and tries to parse a release year from it. 
    Returns the year as an int and the cleaned game name without parantheses 
    (year) block, or the original block
    
    Params:
        folder_name: The folder name or path from which to read the release year
        settings: The Settings object

    Returns:
        year : int | None, just the year as 4 digits
        cleaned_name | game_name : If year extraction succeeds, returns the input name 
            without the parantheses block. If extraction fails, returns original input game or folder name.
    """

    game_name = Path(folder_name).name

    if settings.RELEASE_YEAR_IN_FOLDERNAME:
        match = re.search(r"\s*\((\d{4})\)$", game_name)
        if match:
            year = int(match.group(1))
            cleaned_name = game_name[:match.start()].strip()
            return year, cleaned_name

    return None, game_name

def parse_platform_from_folder_name(
        folder_name: str | Path,
        settings: Settings
        ) -> tuple[str | None, str]:
    """
    Takes the folder name and tries to parse the game platform from it. 

    Params:
        folder_name: str | Path. If the input is a long path 
            (e.g. "/home/user/videos/blablalba") the function will return
            only the game name without the root path

    Returns:
        platform: str | None, the game platform's full, 
            untruncated name. If the platform name in the folder name is a known shorthand defined in
            settings.py, the shorthand will be mapped to the longer version in this func's return.
        game_name: str, the input game (folder) name with the parsed platform prefix removed.


    """
    game_name = Path(folder_name).name
    separator = settings.PLATFORM_PREFIX_SEPARATOR
    game_platforms_map = settings.GAME_PLATFORMS
    default_platform = settings.DEFAULT_PLATFORM

    if settings.PLATFORM_IN_FOLDERNAME and separator in game_name:
        # Split only once so that the separator can also appear in the game name
        prefix, cleaned_name = game_name.split(separator, 1)
        prefix = prefix.strip()

        # Check if the prefix matches a known shorthand
        if prefix in game_platforms_map:
            return game_platforms_map[prefix], cleaned_name.strip()

    # Fallback to DEFAULT_PLATFORM if no valid prefix was found or feature is disabled
    # Looks up default_platform in the dictionary just in case it's a shorthand, otherwise returns it as-is
    resolved_default = game_platforms_map.get(default_platform, default_platform) if default_platform else None

    return resolved_default, game_name

def parse_category_from_folder_name(
        folder_name: str | Path,
        settings: Settings
        ) -> tuple[str | None, str | None, str]:
    """
    Takes the settings and dir name of the footage folder and, if the folder name starts with a known custom category
    prefix, returns both its category and game platform as well as its cleaned up name.
    
    Params:
        folder_name: input folder. Either just the folder name or the full path
        settings: The Settings object.

    Returns:
        category : str or None, if the folder name prefix matches to a known custom category
        platform : str or None, the platform of the mapped category
        cleaned_name : the cleaned name of the game after the parsing operation
    """

    dir_name = Path(folder_name).name
    categories_map = settings.FOOTAGE_FOLDERNAME_CATEGORIES
    separator = settings.PLATFORM_PREFIX_SEPARATOR
    game_platforms = settings.GAME_PLATFORMS

    if settings.FOLDERNAME_CUSTOM_CATEGORIES and categories_map:
        # Sort prefixes by length descending to avoid partial matches (e.g. matching "Doom" before "Doom Mods")
        sorted_prefixes = sorted(categories_map.keys(), key=len, reverse=True)

        for prefix in sorted_prefixes:
            prefix_pattern = prefix + separator
            if dir_name.startswith(prefix_pattern):
                category, platform_key = categories_map[prefix]

                # Remove the category prefix and separator from the folder name
                cleaned_name = dir_name[len(prefix_pattern):].strip()

                # Resolve platform using GAME_PLATFORMS dictionary if it's a shorthand, else use as-is
                resolved_platform = game_platforms.get(platform_key, platform_key) if platform_key else None

                return category, resolved_platform, cleaned_name

    # Return None for category and platform, and the original name if no custom category matched
    return None, None, dir_name

def parse_full_folder_name_data(
        folder_name: Path | str,
        settings:Settings
        ) -> {str, int | None , str | None, str | None}:
    """Takes the settings and the directory name of the game's footage and returns its data split into logical stems.
    
    Returns:
        str: Game name, with the year and category / platform compnents stripped,
            if they have been identified
        int: Release year        
        str: Game platform, platform returned as list
        str: Game category, category returned as list

    Raises:
        FileNotFoundError: if obsidian_path doesn't exist."""

    dir_name = Path(folder_name).name

    release_year = None
    platform = settings.DEFAULT_PLATFORM if settings.DEFAULT_PLATFORM else None
    category = None

    if settings.RELEASE_YEAR_IN_FOLDERNAME:
        release_year, dir_name = parse_release_year_from_folder_name(dir_name, settings)

    if settings.FOLDERNAME_CUSTOM_CATEGORIES:
        category, platform, dir_name = parse_category_from_folder_name(dir_name, settings)

    # Only do the platform deduction if category is unset:
    # only one prefix can be defined in the folder name and if a category is set, it is preferred,
    # the game platform is deduced from the category
    if settings.PLATFORM_IN_FOLDERNAME and not category:
        platform, dir_name = parse_platform_from_folder_name(dir_name, settings)

    game_name = dir_name

    return game_name, release_year, platform, category


def calculate_playtime_from_obsidian_note(obsidian_data_dict: dict, settings: Settings) -> int | None:
    """
    Reads and calculates playtime from parsed obsidian note dictionary.
    Returns:
        pt_mins: int | None. The total playtime as minutes or
            None if time is not set or time in minutes if it can be parsed.
    """

    pt_hours = obsidian_data_dict.get(settings.OBSIDIAN_METADATA_MAP["playtime_hrs"])
    pt_mins = obsidian_data_dict.get(settings.OBSIDIAN_METADATA_MAP["playtime_mins"])

    if pt_hours is None and pt_mins is None:
        return None

    try:
        hours = int(pt_hours) if pt_hours is not None else 0
    except (ValueError, TypeError):
        hours = 0

    try:
        mins = int(pt_mins) if pt_mins is not None else 0
    except (ValueError, TypeError):
        mins = 0

    return (hours * 60) + mins

def validate_rating(rating: str | int | float | None, settings: Settings) -> float | None:
    """Validates the rating and outputs the rating or throws errors if rating is invalid.
    
    Raises:
        TooHighRatingError: If rating too high
        TooLowRatingError: If rating too low
        CannotParseRatingError: If rating invalid

    Returns:
        rating: The validated rating as a float
    """

    if not rating or rating == "":
        return None

    if isinstance(rating, str):
        rating = rating.replace(",",".")

    try:
        rating_standardized = round(float(rating),1)
    except (ValueError ,TypeError) as exc:
        raise CannotParseRatingError(f"Cannot parse rating {rating}") from exc

    min_rating : int = settings.OBSIDIAN_RATING_MIN
    max_rating : int = settings.OBSIDIAN_RATING_MAX

    if rating_standardized > max_rating:
        raise TooHighRatingError(f"Rating {rating} is too high! (Max={max_rating})")
    if rating_standardized < min_rating:
        raise TooLowRatingError(f"Rating {rating} is too low! (Min = {min_rating})")

    if settings.OBSIDIAN_RATING_USE_STAR_SYSTEM: # if true, only accept increments of 0.5
        doubled = rating_standardized * 2
        if not doubled.is_integer():
            raise InvalidStarRatingError(f"Rating {rating} is not a valid star system rating (increment of 0.5)!")

    return rating_standardized

def get_game_metadata(footage_folder_path:Path | str, settings: Settings) -> dict:
    """Get the game's name, release year and platform from the folder name and / or the obsidian database, 
    if one is to be used as per the submitted Settings. 
    If a value can be read from the Obsidian database, it is preferred to anything deduced from the footage folder name. 
    If a value cant be read from Obsidian (due to note not existing, value being invalid or other error), 
    values are populated from the folder name.

    Returns a dictionary, with the following values and datatypes:
    
    Returns:
        game_name : str
        year : int | None
        platforms : []
        categories : []
        genres : []
        rating : int | None
        playtime_mins : int | None
        game_series : str | None
        developers : []
        publishers : []
        md_size : int | None (as kilobytes)
        errors : a separate list from the dictionary with the raised errors
    
    Raises:
        errors: Raised errors are collected to a list and returned
    
    """

    errors = []

    obsidian_path = settings.OBSIDIAN_DB_PATH

    omd = parse_obsidian_note(footage_folder_path, settings, obsidian_path)
    if omd is None:
        omd = {}

    (game_name,
    dir_release_year,
    dir_platform,
    dir_category) = parse_full_folder_name_data(footage_folder_path, settings)

    try:
        game_rating = validate_rating(omd.get(settings.OBSIDIAN_METADATA_MAP["rating"]), settings)
    except (CannotParseRatingError, TooHighRatingError, TooLowRatingError, InvalidStarRatingError) as e:
        errors.append(e)
        game_rating = None

    # Prefer data defined in Obsidian, fallback to data parsed from dir name
    # game_name always parsed from folder name

    # Fallback dir_platform and dir_category are turned into lists;
    # the return value expects the possibility of there being multiple of both,
    # but the data read from folder name can only return single value.

    dir_platform = [dir_platform] if dir_platform else []
    dir_category = [dir_category] if dir_category else []

    metadata = {
        "game_name" : game_name,
        "year" : omd.get(settings.OBSIDIAN_METADATA_MAP["year"],dir_release_year),
        "platforms" : omd.get(settings.OBSIDIAN_METADATA_MAP["platforms"], dir_platform),
        "categories" : omd.get(settings.OBSIDIAN_METADATA_MAP["categories"], dir_category),
        "genres" : omd.get(settings.OBSIDIAN_METADATA_MAP["genres"], []), # Genres never defined in dir name
        "rating" : game_rating,
        "playtime_mins" : calculate_playtime_from_obsidian_note(omd, settings),
        "game_series" : omd.get(settings.OBSIDIAN_METADATA_MAP["game_series"], None),
        "developers" : omd.get(settings.OBSIDIAN_METADATA_MAP["developers"], []),
        "publishers" : omd.get(settings.OBSIDIAN_METADATA_MAP["publishers"], []),
        "md_size" : omd.get("md_file_size", None)
    }



    return metadata, errors


#def sort_footage_folder(
# footage_folder_path:Path,
# video_filetypes: list[str],
# ignored_filetypes: list[str]) -> {list[Path], list[Path], list[Path]}:
# """Recursively scans the footage folder and returns all of the files
# inside of the folder sorted in to three groups: 
# The video files, other files and ignored files."""
#   return None
