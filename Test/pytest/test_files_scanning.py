from utils.scanFiles import (getFootageFolders, parseReleaseYearFromFolderName, parseReleaseYearFromFolderName, parsePlatformFromFolderName, parseCategoryFromFolderName, parseFolderNameData, validateRating, getGameMetadata)
import utils.testHelpers as testHelpers
import os
import pytest
from pathlib import Path
from utils.settingsLoader import Settings
import utils.errors as errors

TESTDATA_DIR = testHelpers.TESTDATA_DIR
TEST_FOOTAGE_DIRECTORY = TESTDATA_DIR/"Gameplay-Footage"
TEST_NOTES_DIRECTORY = TESTDATA_DIR/"Obsidian-Notes"

def test_get_footage_dirs(testdata):

    assert getFootageFolders(TEST_FOOTAGE_DIRECTORY) == [
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
        getFootageFolders(TEST_FOOTAGE_DIRECTORY / "imaginaryfolder")

def test_year_parse(testdata):

    settings = Settings()

    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.SCAN_OBSIDIAN_DB = False

    assert parseReleaseYearFromFolderName("Gone with the wind (1967)",settings) == (1967, "Gone with the wind")
    assert parseReleaseYearFromFolderName("Gone with the (5517) wind (1967)", settings) == (1967, "Gone with the (5517) wind")
    assert parseReleaseYearFromFolderName("Gone with the (557) wind", settings) == (None, "Gone with the (557) wind")
    assert parseReleaseYearFromFolderName(Path(TEST_FOOTAGE_DIRECTORY/"Gone (2020)"),settings) == (2020, str(Path(TEST_FOOTAGE_DIRECTORY / "Gone")))
    assert parseReleaseYearFromFolderName(Path(TEST_FOOTAGE_DIRECTORY/"SNES - Game 6 (1996)"),settings) == (1996, str(Path(TEST_FOOTAGE_DIRECTORY / "SNES - Game 6" )))


    settings.RELEASE_YEAR_IN_FOLDERNAME = False

    assert parseReleaseYearFromFolderName("Gone with the wind (1967)", settings) == (None, "Gone with the wind (1967)")

def test_folder_platform_parse():

    settings = Settings()

    settings.PLATFORM_IN_FOLDERNAME = True
    settings.PLATFORM_PREFIX_SEPARATOR = " - "
    settings.DEFAULT_PLATFORM = "PC"
    settings.GAME_PLATFORMS = {
    "00" : "Not a game",
    "Arcade" : "Pelihallipelit",
    "Atari 2600" : "Atari 2600",
    "CDi" : "Philips CD-i",
    "DOS" : "MS-DOS",
    "Dreamcast" : "Sega Dreamcast",
    "GB" : "Nintendo Game Boy",
    "GBA" : "Nintendo Game Boy Advance",
    "GBC" : "Nintendo Game Boy Color",
    "Lautapelit" : "Lautapelit",
    "Mobiilipelit" : "Mobiilipelit",
    "N64" : "Nintendo 64",
    "NES" : "Nintendo Entertainment System",
    "NGC" : "Nintendo Gamecube",
    "PICO-8" : "Pico-8",
    "PS2" : "Sony Playstation 2",
    "PSX" : "Sony Playstation",
    "Sega Genesis" : "Sega Genesis",
    "Sega Saturn" : "Sega Saturn",
    "SNES" : "Super Nintendo Entertainment System",
    "TIC-80" : "TIC-80",
    "XBOX" : "XBox",
    "Virtual Boy" : "Nintendo Virtual Boy",
    "Web" : "Browser",
    "XYZ" : "Custom defined game platform"
}

    assert parsePlatformFromFolderName("Web - Testipeli (2002)", settings) == ("Browser", "Testipeli (2002)")

    assert parsePlatformFromFolderName("XYZ - Test (1999)", settings) == ("Custom defined game platform", "Test (1999)")

    settings.PLATFORM_IN_FOLDERNAME = False
    settings.DEFAULT_PLATFORM = "CustomPl"

    assert parsePlatformFromFolderName("XYZ - Test (1999)", settings) == ("CustomPl", "XYZ - Test (1999)")

def test_folder_year_parse():
    
    settings = Settings()

    settings.RELEASE_YEAR_IN_FOLDERNAME = True

    assert parseReleaseYearFromFolderName("Web - Nginx (2005)", settings) == (2005, "Web - Nginx")

    settings.RELEASE_YEAR_IN_FOLDERNAME = False

    assert parseReleaseYearFromFolderName("Web - Nginx (2005)", settings) == (None, "Web - Nginx (2005)")

def test_folder_category_parse():

    settings = Settings()

    settings.FOLDERNAME_CUSTOM_CATEGORIES = True
    settings.FOOTAGE_FOLDERNAME_CATEGORIES = {
        "MC Mods" : ("Minecraft mods","Xbox"),
    }

    assert parseCategoryFromFolderName("MC Mods - Scavenging", settings) == ("Minecraft mods", "Xbox", "Scavenging")

def test_folder_category_parse_disabled():

    settings = Settings()

    settings.FOLDERNAME_CUSTOM_CATEGORIES = False

    assert parseCategoryFromFolderName("Doom Mods - Romero Death Skittles (2004)", settings) == (None, None, "Doom Mods - Romero Death Skittles (2004)")

def test_full_folder_metadata_scans_():

    settings = Settings()

    settings.DEFAULT_PLATFORM = "PC"
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.PLATFORM_IN_FOLDERNAME = True
    settings.FOLDERNAME_CUSTOM_CATEGORIES = True

    folder_1 = "Doom Mods - Revenant Bus (2018)"
    folder_2 = "GBA - Pokemon Emerald (2004)"
    folder_3 = "Helsinki Media - Lauri Luuranko (1998)" # not defined as a custom category!
    folder_4 = "Hollow Knight (2007)"

    # (Game name, release year, platform, category)
    assert parseFolderNameData(folder_1, settings) == ("Revenant Bus", 2018, "PC", "Doom Mod")
    assert parseFolderNameData(folder_2, settings) == ("Pokemon Emerald", 2004, "Nintendo Game Boy Advance", None)
    assert parseFolderNameData(folder_3, settings) == ("Helsinki Media - Lauri Luuranko", 1998, "PC", None)        
    assert parseFolderNameData(folder_4, settings) == ("Hollow Knight", 2007, "PC", None)

def test_rating_validation():

    settings = Settings()

    assert validateRating("1",settings) == 1.0
    assert validateRating("2",settings) == 2

    assert validateRating(3, settings) == 3
    assert validateRating(3.5, settings) == 3.5
    assert validateRating("4,5", settings) == 4.5

def test_rating_validation_errors():

    settings = Settings()

    with pytest.raises(errors.CannotParseRatingError):
        assert validateRating("1,5,5",settings)

    with pytest.raises(errors.TooHighRatingError):
        assert validateRating(6, settings)

    with pytest.raises(errors.TooLowRatingError):
        assert validateRating(-1, settings)

    settings.OBSIDIAN_RATING_USE_STAR_SYSTEM = False

    assert validateRating(4.3, settings) == 4.3

    settings.OBSIDIAN_RATING_USE_STAR_SYSTEM = True

    with pytest.raises(errors.InvalidStarRatingError):
        assert validateRating(4.3, settings)


def test_full_metadata_fetch(testdata):

    settings = Settings()

    settings.DEFAULT_PLATFORM = "PC"
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.PLATFORM_IN_FOLDERNAME = True
    settings.FOLDERNAME_CUSTOM_CATEGORIES = True
    settings.FOOTAGE_FOLDERNAME_CATEGORIES = {
        "MC Mods" : ("Minecraft mods","Xbox"),
    }
    settings.SCAN_OBSIDIAN_DB = True
    settings.OBSIDIAN_DB_PATH = TEST_NOTES_DIRECTORY
    settings.GAME_PLATFORMS = {
    "00" : "Not a game",
    "Arcade" : "Pelihallipelit",
    "Atari 2600" : "Atari 2600",
    "CDi" : "Philips CD-i",
    "DOS" : "MS-DOS",
    "Dreamcast" : "Sega Dreamcast",
    "GB" : "Nintendo Game Boy",
    "GBA" : "Nintendo Game Boy Advance",
    "GBC" : "Nintendo Game Boy Color",
    "Lautapelit" : "Lautapelit",
    "Mobiilipelit" : "Mobiilipelit",
    "N64" : "Nintendo 64",
    "NES" : "Nintendo Entertainment System",
    "NGC" : "Nintendo Gamecube",
    "PICO-8" : "Pico-8",
    "PS2" : "Sony Playstation 2",
    "PSX" : "Sony Playstation",
    "Sega Genesis" : "Sega Genesis",
    "Sega Saturn" : "Sega Saturn",
    "SNES" : "Super Nintendo Entertainment System",
    "TIC-80" : "TIC-80",
    "XBOX" : "XBox",
    "Virtual Boy" : "Nintendo Virtual Boy",
    "Web" : "Browser",
    "XYZ" : "Custom defined game platform"
    }

    footageFolder1 = TEST_FOOTAGE_DIRECTORY / "Game 1"
    g1_metadata, errors1 = getGameMetadata(footageFolder1, settings)

    assert g1_metadata.get("year") == 1822 # from the md file
    assert g1_metadata.get("genres") == ["Räiskintä"] # from the md file
    assert g1_metadata.get("platforms") == ["Sega Genesis"] # from the md file
    assert g1_metadata.get("playtime_mins") == 408
    assert 0 < g1_metadata.get("md_size") < 0.23
    assert g1_metadata.get("rating") == None # invalid rating
    assert isinstance(errors1[0],errors.TooHighRatingError) # specifically, too high rating error

def test_full_metadata_no_markdown_file(testdata):

    settings = Settings()

    settings.DEFAULT_PLATFORM = "PC"
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.PLATFORM_IN_FOLDERNAME = True
    settings.FOLDERNAME_CUSTOM_CATEGORIES = True
    settings.FOOTAGE_FOLDERNAME_CATEGORIES = {
        "MC Mods" : ("Minecraft mods","Xbox"),
    }
    settings.SCAN_OBSIDIAN_DB = True
    settings.OBSIDIAN_DB_PATH = TEST_NOTES_DIRECTORY
    settings.GAME_PLATFORMS = {
    "00" : "Not a game",
    "Arcade" : "Pelihallipelit",
    "Atari 2600" : "Atari 2600",
    "CDi" : "Philips CD-i",
    "DOS" : "MS-DOS",
    "Dreamcast" : "Sega Dreamcast",
    "GB" : "Nintendo Game Boy",
    "GBA" : "Nintendo Game Boy Advance",
    "GBC" : "Nintendo Game Boy Color",
    "Lautapelit" : "Lautapelit",
    "Mobiilipelit" : "Mobiilipelit",
    "N64" : "Nintendo 64",
    "NES" : "Nintendo Entertainment System",
    "NGC" : "Nintendo Gamecube",
    "PICO-8" : "Pico-8",
    "PS2" : "Sony Playstation 2",
    "PSX" : "Sony Playstation",
    "Sega Genesis" : "Sega Genesis",
    "Sega Saturn" : "Sega Saturn",
    "SNES" : "Super Nintendo Entertainment System",
    "TIC-80" : "TIC-80",
    "XBOX" : "XBox",
    "Virtual Boy" : "Nintendo Virtual Boy",
    "Web" : "Browser",
    "XYZ" : "Custom defined game platform"
    }

    footagedir = TEST_FOOTAGE_DIRECTORY / "Game 3 (1997)"
    metadata, errors = getGameMetadata(footagedir, settings)

    # matching markdown file doesn't exist for this test footage
    assert metadata.get("year") == 1997
    assert metadata.get("platforms") == ["PC"] # default
    assert metadata.get("rating") == None
    assert metadata.get("categories") == []
    assert metadata.get("genres") == []
    assert metadata.get("playtime_mins") == None
    assert metadata.get("game_series") == None
    assert metadata.get("developers") == []
    assert metadata.get("publishers") == []
    assert metadata.get("md_size") == None

def test_misspelled_platform_folder_name(testdata):

    settings = Settings()

    settings.DEFAULT_PLATFORM = "PC"
    settings.RELEASE_YEAR_IN_FOLDERNAME = True
    settings.PLATFORM_IN_FOLDERNAME = True
    settings.FOLDERNAME_CUSTOM_CATEGORIES = True
    settings.FOOTAGE_FOLDERNAME_CATEGORIES = {
        "MC Mods" : ("Minecraft mods","Xbox"),
    }
    settings.SCAN_OBSIDIAN_DB = True
    settings.OBSIDIAN_DB_PATH = TEST_NOTES_DIRECTORY
    settings.GAME_PLATFORMS = {
    "00" : "Not a game",
    "Arcade" : "Pelihallipelit",
    "Atari 2600" : "Atari 2600",
    "CDi" : "Philips CD-i",
    "DOS" : "MS-DOS",
    "Dreamcast" : "Sega Dreamcast",
    "GB" : "Nintendo Game Boy",
    "GBA" : "Nintendo Game Boy Advance",
    "GBC" : "Nintendo Game Boy Color",
    "Lautapelit" : "Lautapelit",
    "Mobiilipelit" : "Mobiilipelit",
    "N64" : "Nintendo 64",
    "NES" : "Nintendo Entertainment System",
    "NGC" : "Nintendo Gamecube",
    "PICO-8" : "Pico-8",
    "PS2" : "Sony Playstation 2",
    "PSX" : "Sony Playstation",
    "Sega Genesis" : "Sega Genesis",
    "Sega Saturn" : "Sega Saturn",
    "SNES" : "Super Nintendo Entertainment System",
    "TIC-80" : "TIC-80",
    "XBOX" : "XBox",
    "Virtual Boy" : "Nintendo Virtual Boy",
    "Web" : "Browser",
    "XYZ" : "Custom defined game platform"
    }

    footagedir = TEST_FOOTAGE_DIRECTORY / "PSZ - Game 7 (1998)"
    metadata, errors = getGameMetadata(footagedir, settings)

    