from utils.scanFiles import (getFootageFolders, parseReleaseYearFromFolderName, parseReleaseYearFromFolderName, parsePlatformFromFolderName, parseCategoryFromFolderName, parseFolderNameData, validateRating, getGameMetadata)
import os
import pytest
from pathlib import Path
from utils.settingsLoader import Settings
import utils.errors as errors

"""
footage_dir, settings, testdata and notes_dir fixtures are defined in conftest.py.

settings is a fresh Settings object for each test, so the test can override values they are testing for

"""

def test_get_footage_dirs(footage_dir):
 
    assert getFootageFolders(footage_dir) == [
        "Game 1",
        "Game 2 (2002)",
        "Game 3 (1997)",
        "N64 - Game 4 (1999)",
        "NES - Game 5 (1982)",
        "PS2 - Game 8 (2002)",
        "PSZ - Game 7 (1998)",
        "SNES - Game 6 (1996)",
    ]
 
    with pytest.raises(FileNotFoundError):
        getFootageFolders(footage_dir / "imaginaryfolder")


def test_year_parse(settings, footage_dir):
 
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.SCAN_OBSIDIAN_DB = False
 
    assert parseReleaseYearFromFolderName("Gone with the wind (1967)", settings) == (1967, "Gone with the wind")
    assert parseReleaseYearFromFolderName("Gone with the (5517) wind (1967)", settings) == (1967, "Gone with the (5517) wind")
    assert parseReleaseYearFromFolderName("Gone with the (557) wind", settings) == (None, "Gone with the (557) wind")
    assert parseReleaseYearFromFolderName(Path(footage_dir / "Gone (2020)"), settings) == (2020, str(footage_dir / "Gone"))
    assert parseReleaseYearFromFolderName(Path(footage_dir / "SNES - Game 6 (1996)"), settings) == (1996, str(footage_dir / "SNES - Game 6"))
 

def test_year_in_gamename_if_release_in_foldername_false(settings, footage_dir):

    settings.RELEASE_YEAR_IN_FOLDERNAME = False
    settings.SCAN_OBSIDIAN_DB = False
 
    assert parseReleaseYearFromFolderName("Gone with the wind (1967)", settings) == (None, "Gone with the wind (1967)")


def test_folder_platform_parse(settings):
 
    assert parsePlatformFromFolderName("Web - Testipeli (2002)", settings) == ("Browser", "Testipeli (2002)")
    assert parsePlatformFromFolderName("SNES - Test (1999)", settings) == ("Super Nintendo Entertainment System", "Test (1999)")
 
    settings.PLATFORM_IN_FOLDERNAME = False

    assert parsePlatformFromFolderName("SNES - Test (1999)", settings) == ("PC", "SNES - Test (1999)")
 
 
def test_custom_default_platform_assignment(settings, footage_dir):

    settings.GAME_PLATFORMS["XYZ"] = "Custom defined game platform"
    settings.DEFAULT_PLATFORM = "XYZ"

    assert parsePlatformFromFolderName("XYZ - Test (1999)", settings) == ("Custom defined game platform", "Test (1999)")


def test_folder_year_parse(settings):
 
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
 
    assert parseReleaseYearFromFolderName("Web - Nginx (2005)", settings) == (2005, "Web - Nginx")
 
    settings.RELEASE_YEAR_IN_FOLDERNAME = False
 
    assert parseReleaseYearFromFolderName("Web - Nginx (2005)", settings) == (None, "Web - Nginx (2005)")


def test_folder_category_parse(settings):

    # if a match is not made, neither the category or platform is returned
    assert parseCategoryFromFolderName("MC Mods - Scavenging", settings) == (None, None, "MC Mods - Scavenging")

    assert parseCategoryFromFolderName("Doom Mods - Romero Death Skittles (2003)",settings) == ("Doom mod", "PC", "Romero Death Skittles (2003)")


def test_folder_category_parse_disabled(settings):
 
    settings.FOLDERNAME_CUSTOM_CATEGORIES = False
 
    assert parseCategoryFromFolderName("Doom Mods - Romero Death Skittles (2004)", settings) == (None, None, "Doom Mods - Romero Death Skittles (2004)")


def test_full_folder_metadata_scans(settings):
 
    # Returns (Game name, release year, platform, category)
    folder_1 = "Doom Mods - Revenant Bus (2018)"
    assert parseFolderNameData(folder_1, settings) == ("Revenant Bus", 2018, "PC", "Doom mod")

    folder_2 = "GBA - Pokemon Emerald (2004)"
    assert parseFolderNameData(folder_2, settings) == ("Pokemon Emerald", 2004, "Nintendo Game Boy Advance", None)

    folder_3 = "Hollow Knight (2007)"
    assert parseFolderNameData(folder_3, settings) == ("Hollow Knight", 2007, "PC", None)

def test_full_folder_metadata_scans_undefined_custom_category(settings):
    folder = "Helsinki Media - Lauri Luuranko (1998)"  # not defined as a custom category!
    assert parseFolderNameData(folder, settings) == ("Helsinki Media - Lauri Luuranko", 1998, "PC", None)


def test_rating_validation(settings):
 
    assert validateRating("1", settings) == 1.0
    assert validateRating("2", settings) == 2
 
    assert validateRating(3, settings) == 3
    assert validateRating(3.5, settings) == 3.5
    assert validateRating("4,5", settings) == 4.5

def test_rating_validation_comma_decimals(settings):

    assert validateRating("4,5", settings) == 4.5

    assert validateRating("4,",settings) == 4

    assert validateRating("3,0",settings) == 3
    assert validateRating("3,0",settings) == 3.0


def test_rating_validation_errors(settings):
 
    with pytest.raises(errors.CannotParseRatingError):
        assert validateRating("1,5,5", settings)
 
    with pytest.raises(errors.TooHighRatingError):
        assert validateRating(6, settings)
 
    with pytest.raises(errors.TooLowRatingError):
        assert validateRating(-1, settings)
 
    settings.OBSIDIAN_RATING_USE_STAR_SYSTEM = False
 
    assert validateRating(4.3, settings) == 4.3
 
    settings.OBSIDIAN_RATING_USE_STAR_SYSTEM = True
 
    with pytest.raises(errors.InvalidStarRatingError):
        assert validateRating(4.3, settings)

    with pytest.raises(errors.InvalidStarRatingError):
        assert validateRating("4,3", settings)


def test_metadata_gamename(settings, footage_dir):
 
    game = footage_dir / "N64 - Game 5 (1999)"
    metadata, scan_errors = getGameMetadata(game, settings)
 
    assert metadata["gamename"] == "Game 5"


def test_full_metadata_fetch_from_md_file(settings, footage_dir):
 
    footage_folder_1 = footage_dir / "Game 1"
    g1_metadata, scan_errors = getGameMetadata(footage_folder_1, settings)
 
    assert g1_metadata["year"] == 1822  # from the md file
    assert g1_metadata["genres"] == ["Räiskintä"]  # from the md file
    assert g1_metadata["platforms"] == ["Sega Genesis"]  # from the md file
    assert g1_metadata["playtime_mins"] == 408
    assert 0 < g1_metadata["md_size"] < 0.23
    assert g1_metadata["rating"] == None  # invalid rating
    assert isinstance(scan_errors[0], errors.TooHighRatingError)  # specifically, too high rating error


def test_full_metadata_no_markdown_file(settings, footage_dir):
 
    footage_folder = footage_dir / "Game 3 (1997)"
    metadata, scan_errors = getGameMetadata(footage_folder, settings)
 
    # matching markdown file doesn't exist for this test footage
    assert metadata["year"] == 1997
    assert metadata["platforms"] == ["PC"]  # default
    assert metadata["rating"] == None
    assert metadata["categories"] == []
    assert metadata["genres"] == []
    assert metadata["playtime_mins"] == None
    assert metadata["game_series"] == None
    assert metadata["developers"] == []
    assert metadata["publishers"] == []
    assert metadata["md_size"] == None
    assert isinstance(metadata["developers"], list)
 

def test_misspelled_platform_folder_name(settings, footage_dir):
 
    footage_folder = footage_dir / "PSZ - Game 7 (1998)"
    metadata, scan_errors = getGameMetadata(footage_folder, settings)
 
    assert metadata["gamename"] == "PSZ - Game 7"


# TODO: separate tests for individual components
# TODO: test game name identification
## TODO: test year identification
# TODO: test platform identification
# TODO: test category identification

def test_get_gamename_from_folder(settings, footage_dir):
 
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.PLATFORM_IN_FOLDERNAME = True
 
    footage_folder = footage_dir / "N64 - Game 4 (1999)"
    metadata, scan_errors = getGameMetadata(footage_folder, settings)

    assert metadata["gamename"] == "Game 4"

    footage_folder = footage_dir / "PS2 - Game 8 (2002)"
    metadata, scan_errors = getGameMetadata(footage_folder, settings)

    assert metadata["gamename"] == "Game 8"

    