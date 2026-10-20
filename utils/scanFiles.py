import os
from pathlib import Path
from utils.settingsLoader import Settings
from utils.parseObsidianNotes import parseObsidianNote, getObsidianNoteFileSize
from utils.errors import (TooHighRatingError, TooLowRatingError, CannotParseRatingError, InvalidStarRatingError)
import re

def getFootageFolders(directory:str) -> list[str]:
    """Get the list of folders inside the root path in alphabetical order. Does not return absolute paths, only the folder names."""
    return sorted(
        item for item in os.listdir(directory)
        if os.path.isdir(os.path.join(directory,item))
        )

#def GetFootagePath(folder:str) -> list[Path]:

def parseReleaseYearFromFolderName(folderName:str | Path, settings: Settings) -> tuple[int | None, str]:
    """Takes the folder name and tries to parse a release year from it. Returns the year as an int and the cleaned game name without parantheses (year) block, or the original block"""

    gamename = str(folderName).strip()
    yearInFolderName = settings.RELEASE_YEAR_IN_FOLDERNAME

    if yearInFolderName:
        match = re.search(r"\s*\((\d{4})\)$", gamename)
        if match:
            year = int(match.group(1))
            cleaned_name = gamename[:match.start()].strip()
            return year, cleaned_name
        
    return None, gamename

def parsePlatformFromFolderName(folderName: str | Path, settings: Settings) -> tuple[str | None, str]:
    """Takes the folder name and tries to parse the game platform from it. 
    Returns the game platform's full, untruncated name and the cleaned up folder name.
    """
    gamename = str(folderName).strip()
    platformInFolderName = settings.PLATFORM_IN_FOLDERNAME
    separator = settings.PLATFORM_PREFIX_SEPARATOR
    gamePlatformsMap = settings.GAME_PLATFORMS
    defaultPlatform = settings.DEFAULT_PLATFORM

    if platformInFolderName and separator in gamename:
        # Split only once so that the separator can also appear in the game name
        prefix, cleaned_name = gamename.split(separator, 1)
        prefix = prefix.strip()
        
        # Check if the prefix matches a known shorthand (case-insensitive option can be added if needed)
        if prefix in gamePlatformsMap:
            return gamePlatformsMap[prefix], cleaned_name.strip()

    # Fallback to DEFAULT_PLATFORM if no valid prefix was found or feature is disabled
    # Looks up default_platform in the dictionary just in case it's a shorthand, otherwise returns it as-is
    resolved_default = gamePlatformsMap.get(defaultPlatform, defaultPlatform) if defaultPlatform else None
    
    return resolved_default, gamename

def parseCategoryFromFolderName(folderName: str | Path, settings: Settings) -> tuple[str | None, str | None, str]:
    """Takes the settings and dir name of the footage folder and, if the folder name starts with a known custom category prefix, returns both its category and game platform as well as its cleaned up name."""

    dirName = str(folderName).strip()
    customCategoriesEnabled = getattr(settings, "FOLDERNAME_CUSTOM_CATEGORIES", True)
    categoriesMap = getattr(settings, "FOOTAGE_FOLDERNAME_CATEGORIES", {})
    separator = getattr(settings, "PLATFORM_PREFIX_SEPARATOR", " - ")
    gamePlatforms = getattr(settings, "GAME_PLATFORMS", {})

    if customCategoriesEnabled and categoriesMap:
        # Sort prefixes by length descending to avoid partial matches (e.g. matching "Doom" before "Doom Mods")
        sorted_prefixes = sorted(categoriesMap.keys(), key=len, reverse=True)
        
        for prefix in sorted_prefixes:
            prefix_pattern = prefix + separator
            if dirName.startswith(prefix_pattern):
                category, platform_key = categoriesMap[prefix]
                
                # Remove the category prefix and separator from the folder name
                cleaned_name = dirName[len(prefix_pattern):].strip()
                
                # Resolve platform using GAME_PLATFORMS dictionary if it's a shorthand, else use as-is
                resolved_platform = gamePlatforms.get(platform_key, platform_key) if platform_key else None
                
                return category, resolved_platform, cleaned_name

    # Return None for category and platform, and the original name if no custom category matched
    return None, None, dirName

def parseFolderNameData(folderName: Path | str, settings:Settings) -> {str, int | None , str | None, str | None}:
    """Takes the settings and the directory name of the game's footage and returns its data split into logical stems.
    
    Returns:
        str: Game Name
        int: Release year        
        str: Game platform
        str: Game category
    Raises:
        FileNotFoundError: if obsidian_path doesn't exist."""

    dirName = Path(folderName).name

    yearInDirName = settings.RELEASE_YEAR_IN_FOLDERNAME
    platformInDirName = settings.PLATFORM_IN_FOLDERNAME
    releaseYear = None
    platform = settings.DEFAULT_PLATFORM if settings.DEFAULT_PLATFORM else None
    category = None
    categoryInFolder = settings.FOLDERNAME_CUSTOM_CATEGORIES


    if yearInDirName:
        releaseYear, dirName = parseReleaseYearFromFolderName(dirName, settings)

    if categoryInFolder:
        category, platform, dirName = parseCategoryFromFolderName(dirName, settings)
        pass

    # Only do the platform deduction if category is unset: only one prefix is read from the folder name and if a category is set, it is preferred
    if platformInDirName and not category:
        platform, dirName = parsePlatformFromFolderName(dirName, settings)

    gameName = dirName

    return gameName, releaseYear, platform, category


def calculatePlayTime(obsidian_data_dict: dict, settings: Settings) -> int | None:
    """Calculate playtime from parsed obsidian note dictionary. Return None if time is not set or time in minutes if it can be parsed."""

    ptHours = obsidian_data_dict.get(settings.OBSIDIAN_METADATA_MAP["playtime_hrs"])
    ptMins = obsidian_data_dict.get(settings.OBSIDIAN_METADATA_MAP["playtime_mins"])

    if ptHours is None and ptMins is None:
        return None

    try:
        hours = int(ptHours) if ptHours is not None else 0
    except (ValueError, TypeError):
        hours = 0

    try:
        mins = int(ptMins) if ptMins is not None else 0
    except (ValueError, TypeError):
        mins = 0

    return (hours * 60) + mins

def validateRating(rating: str | int | float | None, settings: Settings) -> float | None:
    """Validates the rating and outputs the rating or throws errors if rating is invalid.
    
    Raises:
        TooHighRatingError: If rating too high
        TooLowRatingError: If rating too low
        CannotParseRatingError: If rating invalid
    """

    if not rating or rating == "":
        return None

    if isinstance(rating, str):
        rating = rating.replace(",",".")

    try:
        ratingStandardized = round(float(rating),1)
    except (ValueError ,TypeError):
        raise CannotParseRatingError(f"Cannot parse rating {rating}")
    
    starSystem : bool = settings.OBSIDIAN_RATING_USE_STAR_SYSTEM # if true, only accept increments of 0.5
    minRating : int = settings.OBSIDIAN_RATING_MIN
    maxRating : int = settings.OBSIDIAN_RATING_MAX

    if ratingStandardized > maxRating:
        raise TooHighRatingError(f"Rating {rating} is too high! (Max={maxRating})")
    if ratingStandardized < minRating:
        raise TooLowRatingError(f"Rating {rating} is too low! (Min = {minRating})")

    if starSystem:
        doubled = ratingStandardized * 2
        if not doubled.is_integer():
            raise InvalidStarRatingError(f"Rating {rating} is not a valid star system rating (increment of 0.5)!")

    return ratingStandardized

def getGameMetadata(footage_folder_path:Path | str, settings: Settings | None = None) -> dict:
    """Get the game's name, release year and platform from the folder name and / or the obsidian database, if one is to be used as per the submitted Settings. If a value can be read from the Obsidian database, it is preferred to anything deduced from the footage folder name. If a value cant be read from Obsidian (due to note not existing, value being invalid or other error), values are populated from the folder name.

    Returns a dictionary, with the following values and datatypes:
    
    Returns:
        gamename : str
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
    """

    errors = []



    if settings == None:
        raise ValueError("Game metadata parsing failed due to no settings being passed to the func.")

    obsidian_path = settings.OBSIDIAN_DB_PATH

    omd = parseObsidianNote(footage_folder_path, settings, obsidian_path)
    if omd is None:
        omd = {}

    gameName, dirReleaseYear, dirPlatform, dirCategory = parseFolderNameData(footage_folder_path, settings)

    ## From this point on the platform and category are standardized as lists; if platform and/or category is read from dir name, they are treated as single-item lists

    dirPlatform = [dirPlatform] if dirPlatform else []
    dirCategory = [dirCategory] if dirCategory else []

    try:
        gameRating = validateRating(omd.get(settings.OBSIDIAN_METADATA_MAP["rating"]), settings)
    except (CannotParseRatingError, TooHighRatingError, TooLowRatingError, InvalidStarRatingError) as e:
        errors.append(e)
        gameRating = None
    
    metadata = {
        "gamename" : gameName,
        "year" : omd.get(settings.OBSIDIAN_METADATA_MAP["year"],dirReleaseYear), # Prefer year defined in Obsidian, fallback to year parsed from dir name
        "platforms" : omd.get(settings.OBSIDIAN_METADATA_MAP["platforms"], dirPlatform),
        "categories" : omd.get(settings.OBSIDIAN_METADATA_MAP["categories"], dirCategory),
        "genres" : omd.get(settings.OBSIDIAN_METADATA_MAP["genres"], []), # Genres never defined in dir name
        "rating" : gameRating,
        "playtime_mins" : calculatePlayTime(omd, settings),
        "game_series" : omd.get(settings.OBSIDIAN_METADATA_MAP["game_series"], None),
        "developers" : omd.get(settings.OBSIDIAN_METADATA_MAP["developers"], []),
        "publishers" : omd.get(settings.OBSIDIAN_METADATA_MAP["publishers"], []),
        "md_size" : omd.get("md_file_size", None)
    }


    return metadata, errors

def sortFootageFolder(footage_folder_path:Path, video_filetypes: list[str], ignored_filetypes: list[str]) -> {list[Path], list[Path], list[Path]}:
    """Recursively scans the footage folder and returns all of the files inside of the folder sorted in to three groups: The video files, other files and ignored files."""
    pass