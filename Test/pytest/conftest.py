import pytest
from utils.testHelpers import UnpackTests, ValidateTestFiles, DeleteTestFiles

@pytest.fixture(scope="session")
def testdata():
    UnpackTests()
    try:
        ValidateTestFiles()
        yield
    finally:
        DeleteTestFiles()
        