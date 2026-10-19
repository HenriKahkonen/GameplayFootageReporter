import os
from pathlib import Path
from utils.settingsLoader import Settings
import re

def GetFootageFolders(directory:str) -> list[str]:
    """Get the list of folders inside the root path in alphabetical order. Does not return absolute paths, only the folder names."""
    return sorted(os.listdir(directory))

#def GetFootagePath(folder:str) -> list[Path]:

def parseReleaseYearFromFolderName(folderName:str | Path, settings: Settings) -> int | None:
    """Takes the folder name and tries to parse a release year from it."""

    gamename = str(folderName)
    yearInFolderName = settings.RELEASE_YEAR_IN_FOLDERNAME

    if yearInFolderName:
        match = re.search(r"\((\d{4})\)$", gamename.strip())
        if match:
            return int(match.group(1))
        
    return None

def parseObsidianNote(folderName:str | Path, settings:Settings, obsidian_path: str | Path) -> dict | None:
    """Try to match the folder name to a matching Obsidian markdown note. If a match is found, return Obsidian's metadata defined in settings as a dictionary."""

    if settings.SCAN_OBSIDIAN_DB == False:
        return None


    pass



#def parseGameplatform

def GetGameMetadata(footage_folder_path:Path | str, obsidian_path: Path | str | None = None, settings: Settings | None = None) -> dict:
    """Get the game's name, release year and platform from the folder name and / or the obsidian database, if one is to be used as per the submitted Settings."""

    if Settings == None:
        raise ValueError("Game metadata parsing failed due to no settings being passed to the func.")

    obsidianMetadata = parseObsidianNote(footage_folder_path,obsidian_path, settings)

    #releaseYear = parseReleaseYearFromFolderName(str(footage_folder_path))

    return {
        "releaseYear" : releaseYear
    }

def SortFootageFolder(footage_folder_path:Path, video_filetypes: list[str], ignored_filetypes: list[str]) -> {list[Path], list[Path], list[Path]}:
    """Recursively scans the footage folder and returns all of the files inside of the folder sorted in to three groups: The video files, other files and ignored files."""
    pass