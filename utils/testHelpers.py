from zipfile import ZipFile
from hashlib import sha256
from pathlib import Path
import os

def UnpackTests():
    """Unpacks the tests' data from the zip directory. The test data includes a few small video files, so they come zipped to save space in the repository."""
    zip_archive_path = Path("./Test/Testdata/Testdata.zip")
    if not os.path.exists(zip_archive_path):
        raise FileNotFoundError(f"The test zip arhive at {zip_archive_path} was not found!")
    with ZipFile(zip_archive_path, 'r') as zObject:
        zObject.extractall(path=Path("./Test/Testdata"))
    pass

def ValidateTestFiles():
    """Check that the files match their expected has values."""
    pass

def DeleteTestFiles():
    """Free up disk space by deleting the unneeded test files."""
    pass