"""Tests regarding scanning obsidian note markdown files."""

from pathlib import Path
from utils.settings_loader import Settings
from utils.parse_obsidian_notes import (
    strip_obsidian_wikilinks,
    build_obsidian_note_index,
    normalize_name,
    read_obsidian_note_frontmatter,
    get_obsidian_note_frontmatter,
    parse_obsidian_note,
    get_file_size,
    get_obsidian_note_filesize
    )

def test_wikilink_strip():

    assert strip_obsidian_wikilinks("[[Testi]]") == "Testi"
    assert strip_obsidian_wikilinks("Testi") == "Testi"
    assert strip_obsidian_wikilinks("Testi]]") == "Testi]]"
    assert strip_obsidian_wikilinks("[[Testi|Alias]]") == "Testi"
    assert strip_obsidian_wikilinks("[[Testi#Otsikko]]") == "Testi"
    assert strip_obsidian_wikilinks("[Ulkoinenlinkki](https://google.com)") == "[Ulkoinenlinkki](https://google.com)"

def test_wikilink_multiple_strip():

    assert strip_obsidian_wikilinks(
        "[[Linkki 1]], minkä jälkeen tulee [[Linkki 2]]"
        ) == "Linkki 1, minkä jälkeen tulee Linkki 2"

def test_obsidian_index_build(notes_dir):

    assert build_obsidian_note_index(notes_dir) == {
        "game 1" : Path(notes_dir / "Game 1.md"),
        "game 2 (2002)" : Path(notes_dir / "Game 2 (2002).md"),
        "nes - game 5 (1982)" : Path(notes_dir / "NES - Game 5 (1982).md"),
        "psx - game 7 (1998)" : Path(notes_dir / "PSX - Game 7 (1998).md"),
        "snes - game 6 (1996)" : Path(notes_dir / "SNES - Game 6 (1996).md")
    }

def test_name_normalization():

    assert normalize_name("    Testi !") == "testi !"
    assert normalize_name("FIle.txt") == "file.txt"
    assert normalize_name("mixed_CASE-123.pdf") == "mixed_case-123.pdf"
    assert normalize_name("\t\n padded_name.txt \r ") == "padded_name.txt"
    assert normalize_name("   ") == ""
    assert normalize_name("") == ""
    assert normalize_name("Test\nNewline") == "test\nnewline"

def test_special_chars_normalization():

    assert normalize_name("Straße") == "strasse"

def test_obsidian_frontmatter_get_nofrontmatter(notes_dir):

    assert get_obsidian_note_frontmatter(Path(notes_dir / "SNES - Game 6 (1996).md")) is None

def test_obsidian_frontmatter_get(notes_dir):

    assert get_obsidian_note_frontmatter(Path(notes_dir / "Game 1.md")) == """year: 1822
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

    note1data = read_obsidian_note_frontmatter(Path(notes_dir / "Game 1.md"))
    note2data = read_obsidian_note_frontmatter(Path(notes_dir / "NES - Game 5 (1982).md"))

    assert note1data["year"] == 1822
    assert note1data["Genret"] == ["Räiskintä"]
    assert note1data["tags"] == ["Peli"]
    assert note1data["Playtime_hrs"] == 6
    assert note1data["Play_Status"] == "[[Status - Playing]]"

    assert note2data["Kehittäjä(t)"] == ["[[id Software]]"]
    assert note2data["Genret"] == ["[[Räiskintä (FPS) -pelit]]","[[Lisäosat]]"]
    assert note2data["Alusta(t)"] == ["[[PC]]","Useilla alustoilla"]

def test_obsidian_frontmatter_datatypes(notes_dir):

    note1data = read_obsidian_note_frontmatter(Path(notes_dir / "Game 1.md"))
    note2data = read_obsidian_note_frontmatter(Path(notes_dir / "NES - Game 5 (1982).md"))

    assert isinstance(note2data["year"], int)
    assert isinstance(note1data["Alusta(t)"], list)
    assert isinstance(note1data["Play_Status"], str)

def test_parse_obsidian_note(notes_dir):

    settings = Settings()
    note1 = parse_obsidian_note("Game 1", settings, notes_dir)

    note2 = parse_obsidian_note("Game 3", settings, notes_dir) # note doesn't exist

    note3 = parse_obsidian_note("SNES - Game 6 (1996)", settings, notes_dir) # note doesn't have valid frontmatter

    assert note2 is None
    assert note3 is None
    assert isinstance(note1,dict)
    assert note1["Rating"] == 6


def test_filesize_check(footage_dir, notes_dir):

    note1size = get_file_size(Path(notes_dir / "Game 1.md"))
    video1size = get_file_size(Path(footage_dir / "Game 3 (1997)" / "game3.MOV"))

    assert note1size > 0
    assert note1size < 0.23
    assert video1size > 3300
    assert video1size < 3320

def test_obsidian_filesize_check(notes_dir, footage_dir):

    note1size = get_obsidian_note_filesize(Path(notes_dir / "Game 1.md"))
    video1size = get_obsidian_note_filesize(Path(footage_dir / "Game 3 (1997)" / "game3.MOV"))

    assert note1size > 0
    assert note1size < 0.23
    assert video1size is None
