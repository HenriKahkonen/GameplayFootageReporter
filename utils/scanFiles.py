import os
from pathlib import Path
from utils.settingsLoader import Settings
import re

def GetFootageFolders(directory:str) -> list[str]:
    """Get the list of folders inside the root path in alphabetical order. Does not return absolute paths, only the folder names."""
    return sorted(os.listdir(directory))

#def GetFootagePath(folder:str) -> list[Path]:

def parseReleaseYearFromFolderName(folderName:str | Path, settings: Settings) -> int | None:
    """Takes the folder name and tries to parse a release year from it. If """

    gamename = str(folderName)
    yearInFolderName = settings.RELEASE_YEAR_IN_FOLDERNAME
    yearCandidate = None

    if yearInFolderName:
        match = re.search(r"\((\d{4})\)$", gamename.strip())
        if match:
            return int(match.group(1))
    return None

#def parseGameplatform

def GetGameMetadata(footage_folder_path:Path, settings: Settings) -> dict:
    """Get the game's name, release year and platform from the folder name and / or the obsidian database, if one is to be used as per the submitted Settings."""

    releaseYear = parseReleaseYearFromFolderName(str(footage_folder_path))
    return {
        "releaseYear" : releaseYear
    }

def SortFootageFolder(footage_folder_path:Path, video_filetypes: list[str], ignored_filetypes: list[str]) -> {list[Path], list[Path], list[Path]}:
    """Recursively scans the footage folder and returns all of the files inside of the folder sorted in to three groups: The video files, other files and ignored files."""
    pass