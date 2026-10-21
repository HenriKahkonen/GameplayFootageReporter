"""Shared fixtures for pytest"""

import json
import hashlib
import shutil
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Generator
from zipfile import ZipFile

import pytest

from utils.settingsLoader import Settings

### Test data locations
REPO_ROOT = Path(__file__).resolve().parents[2]
TESTDATA_DIR = REPO_ROOT / "Test" / "Testdata"
ZIP_ARCHIVE_PATH = TESTDATA_DIR / "Testdata.zip"
SHA256_BASELINE_PATH = TESTDATA_DIR / "sha256validation.json"

FOOTAGE_DIRNAME = "Gameplay-Footage"
NOTES_DIRNAME = "Obsidian-Notes"
TEST_FILE_DIRS = (FOOTAGE_DIRNAME, NOTES_DIRNAME)

# --- Default settings used by the tests --------------------------------------
TEST_GAME_PLATFORMS = {
    "00": "Not a game",
    "Arcade": "Pelihallipelit",
    "Atari 2600": "Atari 2600",
    "CDi": "Philips CD-i",
    "DOS": "MS-DOS",
    "Dreamcast": "Sega Dreamcast",
    "GB": "Nintendo Game Boy",
    "GBA": "Nintendo Game Boy Advance",
    "GBC": "Nintendo Game Boy Color",
    "Lautapelit": "Lautapelit",
    "Mobiilipelit": "Mobiilipelit",
    "N64": "Nintendo 64",
    "NES": "Nintendo Entertainment System",
    "NGC": "Nintendo Gamecube",
    "PICO-8": "Pico-8",
    "PS2": "Sony Playstation 2",
    "PSX": "Sony Playstation",
    "Sega Genesis": "Sega Genesis",
    "Sega Saturn": "Sega Saturn",
    "SNES": "Super Nintendo Entertainment System",
    "TIC-80": "TIC-80",
    "XBOX": "XBox",
    "Virtual Boy": "Nintendo Virtual Boy",
    "Web": "Browser",
}
 
TEST_FOOTAGE_CATEGORIES = {
    "Doom Mods": ("Doom mod", "PC"),
    "Suomipelit": ("Suomipelit","PC"),
}

### Test data helper funcs

def sha256Hash(filepath):
    """Compute the sha256 hash of the file."""
    hash_func = hashlib.sha256()
    with open(filepath, "rb") as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def _collectTestFiles():
    """Return a sorted list of all files inside the test directories."""
    files = []
    for dirName in TEST_FILE_DIRS:
        dirPath = TESTDATA_DIR / dirName
        if dirPath.is_dir():
            files.extend(p for p in dirPath.rglob("*") if p.is_file())
    return sorted(files)

def UnpackTests():
    """Unpacks the tests' data from the zip directory. The test data includes a few small video files, so they come zipped to save space in the repository."""
    if not os.path.exists(ZIP_ARCHIVE_PATH):
        raise FileNotFoundError(f"The test zip arhive at {ZIP_ARCHIVE_PATH} was not found!")
    with ZipFile(ZIP_ARCHIVE_PATH, 'r') as zObject:
        zObject.extractall(path=TESTDATA_DIR)
    pass

def GenerateTestFileValidationBaseline():
    """Generate a file of all the hashes in the directory that can then be compared
    to to validate the test files."""
    files = _collectTestFiles()
    if not files:
        raise FileNotFoundError(
            f"No test files found in {TESTDATA_DIR}. Did you call UnpackTests() first?"
        )
    baseline = {
        p.relative_to(TESTDATA_DIR).as_posix(): sha256Hash(p)
        for p in files
    }
    with open(SHA256_BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2, sort_keys=True)
    return baseline

def ValidateTestFiles():
    """Check that the files match their expected hash values.

    Returns True if everything matches; otherwise raises a ValueError
    describing what is missing, unexpected, or changed.
    """
    if not SHA256_BASELINE_PATH.exists():
        raise FileNotFoundError(f"Baseline file {SHA256_BASELINE_PATH} was not found!")
    with open(SHA256_BASELINE_PATH, "r", encoding="utf-8") as f:
        expected = json.load(f)

    actual_files = {p.relative_to(TESTDATA_DIR).as_posix(): p for p in _collectTestFiles()}

    missing = sorted(set(expected) - set(actual_files))
    unexpected = sorted(set(actual_files) - set(expected))
    mismatched = sorted(
        name for name, path in actual_files.items()
        if name in expected and sha256Hash(path) != expected[name]
    )

    if missing or unexpected or mismatched:
        problems = []
        if missing:
            problems.append(f"Missing files: {missing}")
        if unexpected:
            problems.append(f"Unexpected files: {unexpected}")
        if mismatched:
            problems.append(f"Hash mismatches: {mismatched}")
        raise ValueError("Test file validation failed:\n" + "\n".join(problems))
    return True

def DeleteTestFiles():
    """Free up disk space by deleting the unneeded test files."""
    for dirName in TEST_FILE_DIRS:
        dirPath = TESTDATA_DIR / dirName
        if dirPath.is_dir():
            shutil.rmtree(dirPath)
            print(f"{dirPath} removed.")

#### Pytest additional options

def pytest_addoption(parser):
    parser.addoption(
        "--regen-testdata-baseline",
        action="store_true",
        default=False,
        help="Regenerate sha256validation.json from the unpacked test data instead of validating it.",
    )
    parser.addoption(
        "--delete-testdata",
        action="store_true",
        default=False,
        help="Delete the unpacked test data after the test session.",
    )


### Pytest fixtures

@dataclass(frozen=True)
class DataPaths:
    root: Path
    footage: Path
    notes: Path

@pytest.fixture(scope="session")
def testdata(request) -> Generator[DataPaths, None, None]:
    UnpackTests()
    try:
        if request.config.getoption("--regen-testdata-baseline"):
            GenerateTestFileValidationBaseline()
        else:
            ValidateTestFiles()
        yield DataPaths(
            root=TESTDATA_DIR,
            footage=TESTDATA_DIR / FOOTAGE_DIRNAME,
            notes=TESTDATA_DIR / NOTES_DIRNAME,
        )
    finally:
        if request.config.getoption("--delete-testdata"):
            DeleteTestFiles()

@pytest.fixture(scope="session")
def footage_dir(testdata) -> Path:
    return testdata.footage

@pytest.fixture(scope="session")
def notes_dir(testdata) -> Path:
    return testdata.notes

@pytest.fixture
def settings(footage_dir, notes_dir) -> Settings:
    """A fresh Settings object with the defaults most tests want.
 
    Function-scoped, so tests can change any value without affecting others.
    """
    s = Settings()
 
    s.GAMEPLAY_FOOTAGE_PATH = footage_dir
    s.OBSIDIAN_DB_PATH = notes_dir
    s.SCAN_OBSIDIAN_DB = True
 
    s.DEFAULT_PLATFORM = "PC"
    s.PLATFORM_IN_FOLDERNAME = True
    s.PLATFORM_PREFIX_SEPARATOR = " - "
    s.RELEASE_YEAR_IN_FOLDERNAME = True
    s.GAME_PLATFORMS = dict(TEST_GAME_PLATFORMS)
 
    s.FOLDERNAME_CUSTOM_CATEGORIES = True
    s.FOOTAGE_FOLDERNAME_CATEGORIES = TEST_FOOTAGE_CATEGORIES
 
    s.validate()

    return s
