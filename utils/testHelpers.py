from zipfile import ZipFile
import hashlib
from pathlib import Path
import os
import json
import shutil

def sha256Hash(filepath):
    """Compute the sha256 hash of the file."""
    hash_func = hashlib.sha256()
    with open(filepath, "rb") as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

TEST_FILE_DIRS = [
    "Gameplay-Footage",
    "Obsidian-Notes"
]

TESTDATA_DIR = Path("./Test/Testdata/")
ZIP_ARCHIVE_PATH = TESTDATA_DIR / "Testdata.zip"
SHA256_BASELINE_PATH = TESTDATA_DIR / "sha256validation.json"

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

