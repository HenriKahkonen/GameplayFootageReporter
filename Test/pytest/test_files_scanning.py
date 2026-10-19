from utils.scanFiles import (GetFootageFolders, parseReleaseYearFromFolderName)
import utils.testHelpers as testHelpers
import os
import pytest
from pathlib import Path
from utils.settingsLoader import Settings

TESTDATA_DIR = testHelpers.TESTDATA_DIR
TEST_FOOTAGE_DIRECTORY = TESTDATA_DIR/"Gameplay-Footage"
TEST_NOTES_DIRECTORY = TESTDATA_DIR/"Obsidian-Notes"

def test_get_footage_dirs(testdata):

    assert GetFootageFolders(TEST_FOOTAGE_DIRECTORY) == [
            "Game 1", 
            "Game 2 (2002)", 
            "Game 3 (1997)", 
            "N64 - Game 4 (1999)", 
            "NES - Game 5 (1982)", 
            "PS2 - Game 8 (2002)", 
            "PSZ - Game 7 (1998)", 
            "SNES - Game 6 (1996)"
        ]

    with pytest.raises(FileNotFoundError):
        GetFootageFolders(TEST_FOOTAGE_DIRECTORY / "imaginaryfolder")

def test_year_parse(testdata):

    settings = Settings()

    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.SCAN_OBSIDIAN_DB = False

    assert parseReleaseYearFromFolderName("Gone with the wind (1967)",settings) == 1967
    assert parseReleaseYearFromFolderName("Gone with the (5517) wind (1967)", settings) == 1967
    assert parseReleaseYearFromFolderName("Gone with the (557) wind", settings) == None
    assert parseReleaseYearFromFolderName(Path(TEST_FOOTAGE_DIRECTORY/"Gone (2020)"),settings) == 2020
    assert parseReleaseYearFromFolderName(Path(TEST_FOOTAGE_DIRECTORY/"SNES - Game 6 (1996)"),settings) == 1996


    settings.RELEASE_YEAR_IN_FOLDERNAME = False

    assert parseReleaseYearFromFolderName("Gone with the wind (1967)", settings) == None
