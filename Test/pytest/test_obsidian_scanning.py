from utils.parseObsidianNotes import (stripObsidianWikilinks, buildObsidianNoteIndex, normalizeName, readObsidianFrontmatter, getObsidianFrontmatter, parseObsidianNote, getFileSize, getObsidianNoteFileSize )
import utils.testHelpers as testHelpers
import os
import pytest
from pathlib import Path, PosixPath
from utils.settingsLoader import Settings

TESTDATA_DIR = testHelpers.TESTDATA_DIR
TEST_FOOTAGE_DIRECTORY = TESTDATA_DIR/"Gameplay-Footage"
TEST_NOTES_DIRECTORY = TESTDATA_DIR/"Obsidian-Notes"

def test_wikilink_strip():

    assert stripObsidianWikilinks("[[Testi]]") == "Testi"
    assert stripObsidianWikilinks("Testi") == "Testi"
    assert stripObsidianWikilinks("Testi]]") == "Testi]]"
    assert stripObsidianWikilinks("[[Testi|Alias]]") == "Testi"
    assert stripObsidianWikilinks("[[Testi#Otsikko]]") == "Testi"
    assert stripObsidianWikilinks("[Ulkoinenlinkki](https://google.com)") == "[Ulkoinenlinkki](https://google.com)"

def test_wikilink_multiple_strip():

    assert stripObsidianWikilinks("[[Linkki 1]], minkä jälkeen tulee [[Linkki 2]]") == "Linkki 1, minkä jälkeen tulee Linkki 2"

def test_obsidian_index_build():
    
    assert buildObsidianNoteIndex(TEST_NOTES_DIRECTORY) == {
        "game 1" : Path(TEST_NOTES_DIRECTORY / "Game 1.md"),
        "game 2 (2002)" : Path(TEST_NOTES_DIRECTORY / "Game 2 (2002).md"),
        "nes - game 5 (1982)" : Path(TEST_NOTES_DIRECTORY / "NES - Game 5 (1982).md"),
        "psx - game 7 (1998)" : Path(TEST_NOTES_DIRECTORY / "PSX - Game 7 (1998).md"),
        "snes - game 6 (1996)" : Path(TEST_NOTES_DIRECTORY / "SNES - Game 6 (1996).md")
    }

def test_name_normalization():

    assert normalizeName("    Testi !") == "testi !"
    assert normalizeName("FIle.txt") == "file.txt"
    assert normalizeName("mixed_CASE-123.pdf") == "mixed_case-123.pdf"
    assert normalizeName("\t\n padded_name.txt \r ") == "padded_name.txt"
    assert normalizeName("   ") == ""
    assert normalizeName("") == ""
    assert normalizeName("Test\nNewline") == "test\nnewline"

def test_special_chars_normalization():
    
    assert normalizeName("Straße") == "strasse"

def test_obsidian_frontmatter_get_nofrontmatter():

    assert getObsidianFrontmatter(Path(TEST_NOTES_DIRECTORY / "SNES - Game 6 (1996).md")) == None

def test_obsidian_frontmatter_get():

    assert getObsidianFrontmatter(Path(TEST_NOTES_DIRECTORY / "Game 1.md")) == """year: 1822
Genret: 
  - Räiskintä
tags:
  - Peli
Alusta(t): [[Sega Genesis]]
Playtime_hrs: 6
Playtime_mins: 48
Pelisarja:
Kehittäjä(t):
Julkaisija(t):
Play_Status: "[[Status - Playing]]"
Rating: 6"""


def test_obsidian_frontmatter_read():

    note1data = readObsidianFrontmatter(Path(TEST_NOTES_DIRECTORY / "Game 1.md"))
    note2data = readObsidianFrontmatter(Path(TEST_NOTES_DIRECTORY / "NES - Game 5 (1982).md"))

    assert note1data["year"] == 1822
    assert note1data["Genret"] == ["Räiskintä"]
    assert note1data["tags"] == ["Peli"]
    assert note1data["Playtime_hrs"] == 6
    assert note1data["Play_Status"] == "[[Status - Playing]]"

    assert note2data["Kehittäjä(t)"] == ["[[id Software]]"]
    assert note2data["Genret"] == ["[[Räiskintä (FPS) -pelit]]","[[Lisäosat]]"]
    assert note2data["Alusta(t)"] == ["[[PC]]","Useilla alustoilla"]

def test_obsidian_frontmatter_datatypes():
        
    note1data = readObsidianFrontmatter(Path(TEST_NOTES_DIRECTORY / "Game 1.md"))
    note2data = readObsidianFrontmatter(Path(TEST_NOTES_DIRECTORY / "NES - Game 5 (1982).md"))

    assert isinstance(note2data["year"], int)
    assert isinstance(note1data["Alusta(t)"], list)
    assert isinstance(note1data["Play_Status"], str)

def test_parse_obsidian_note():

    settings = Settings()
    note1 = parseObsidianNote("Game 1", settings, TEST_NOTES_DIRECTORY)

    note2 = parseObsidianNote("Game 3", settings, TEST_NOTES_DIRECTORY) # note doesn't exist

    note3 = parseObsidianNote("SNES - Game 6 (1996)", settings, TEST_NOTES_DIRECTORY) # note doesn't have valid frontmatter

    assert note2 == None
    assert note3 == None
    assert isinstance(note1,dict)
    assert note1["Rating"] == 6


def test_filesize_check():

    note1size = getFileSize(Path(TEST_NOTES_DIRECTORY / "Game 1.md"))
    video1size = getFileSize(Path(TEST_FOOTAGE_DIRECTORY / "Game 3 (1997)" / "game3.MOV"))

    assert note1size > 0
    assert note1size < 0.23
    assert video1size > 3300
    assert video1size < 3320

def test_obsidian_filesize_check():

    note1size = getObsidianNoteFileSize(Path(TEST_NOTES_DIRECTORY / "Game 1.md"))
    video1size = getObsidianNoteFileSize(Path(TEST_FOOTAGE_DIRECTORY / "Game 3 (1997)" / "game3.MOV"))

    assert note1size > 0
    assert note1size < 0.23
    assert video1size == None


