from utils.parseObsidianNotes import (stripObsidianWikilinks, buildObsidianNoteIndex, normalizeName, readObsidianFrontmatter, getObsidianFrontmatter, parseObsidianNote, getFileSize, getObsidianNoteFileSize )
import os
import pytest
from pathlib import Path, PosixPath
from utils.settingsLoader import Settings

def test_wikilink_strip():

    assert stripObsidianWikilinks("[[Testi]]") == "Testi"
    assert stripObsidianWikilinks("Testi") == "Testi"
    assert stripObsidianWikilinks("Testi]]") == "Testi]]"
    assert stripObsidianWikilinks("[[Testi|Alias]]") == "Testi"
    assert stripObsidianWikilinks("[[Testi#Otsikko]]") == "Testi"
    assert stripObsidianWikilinks("[Ulkoinenlinkki](https://google.com)") == "[Ulkoinenlinkki](https://google.com)"

def test_wikilink_multiple_strip():

    assert stripObsidianWikilinks("[[Linkki 1]], minkä jälkeen tulee [[Linkki 2]]") == "Linkki 1, minkä jälkeen tulee Linkki 2"

def test_obsidian_index_build(notes_dir):
    
    assert buildObsidianNoteIndex(notes_dir) == {
        "game 1" : Path(notes_dir / "Game 1.md"),
        "game 2 (2002)" : Path(notes_dir / "Game 2 (2002).md"),
        "nes - game 5 (1982)" : Path(notes_dir / "NES - Game 5 (1982).md"),
        "psx - game 7 (1998)" : Path(notes_dir / "PSX - Game 7 (1998).md"),
        "snes - game 6 (1996)" : Path(notes_dir / "SNES - Game 6 (1996).md")
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

def test_obsidian_frontmatter_get_nofrontmatter(notes_dir):

    assert getObsidianFrontmatter(Path(notes_dir / "SNES - Game 6 (1996).md")) == None

def test_obsidian_frontmatter_get(notes_dir):

    assert getObsidianFrontmatter(Path(notes_dir / "Game 1.md")) == """year: 1822
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


def test_obsidian_frontmatter_read(notes_dir):

    note1data = readObsidianFrontmatter(Path(notes_dir / "Game 1.md"))
    note2data = readObsidianFrontmatter(Path(notes_dir / "NES - Game 5 (1982).md"))

    assert note1data["year"] == 1822
    assert note1data["Genret"] == ["Räiskintä"]
    assert note1data["tags"] == ["Peli"]
    assert note1data["Playtime_hrs"] == 6
    assert note1data["Play_Status"] == "[[Status - Playing]]"

    assert note2data["Kehittäjä(t)"] == ["[[id Software]]"]
    assert note2data["Genret"] == ["[[Räiskintä (FPS) -pelit]]","[[Lisäosat]]"]
    assert note2data["Alusta(t)"] == ["[[PC]]","Useilla alustoilla"]

def test_obsidian_frontmatter_datatypes(notes_dir):
        
    note1data = readObsidianFrontmatter(Path(notes_dir / "Game 1.md"))
    note2data = readObsidianFrontmatter(Path(notes_dir / "NES - Game 5 (1982).md"))

    assert isinstance(note2data["year"], int)
    assert isinstance(note1data["Alusta(t)"], list)
    assert isinstance(note1data["Play_Status"], str)

def test_parse_obsidian_note(notes_dir):

    settings = Settings()
    note1 = parseObsidianNote("Game 1", settings, notes_dir)

    note2 = parseObsidianNote("Game 3", settings, notes_dir) # note doesn't exist

    note3 = parseObsidianNote("SNES - Game 6 (1996)", settings, notes_dir) # note doesn't have valid frontmatter

    assert note2 == None
    assert note3 == None
    assert isinstance(note1,dict)
    assert note1["Rating"] == 6


def test_filesize_check(footage_dir, notes_dir):

    note1size = getFileSize(Path(notes_dir / "Game 1.md"))
    video1size = getFileSize(Path(footage_dir / "Game 3 (1997)" / "game3.MOV"))

    assert note1size > 0
    assert note1size < 0.23
    assert video1size > 3300
    assert video1size < 3320

def test_obsidian_filesize_check(notes_dir, footage_dir):

    note1size = getObsidianNoteFileSize(Path(notes_dir / "Game 1.md"))
    video1size = getObsidianNoteFileSize(Path(footage_dir / "Game 3 (1997)" / "game3.MOV"))

    assert note1size > 0
    assert note1size < 0.23
    assert video1size == None


