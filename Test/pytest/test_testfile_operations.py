import utils.testHelpers as testHelpers

import utils.testHelpers as testHelpers
import pytest

TESTDATA_DIR = testHelpers.TESTDATA_DIR
TEST_FOOTAGE_DIRECTORY = TESTDATA_DIR/"Gameplay-Footage"
TEST_NOTES_DIRECTORY = TESTDATA_DIR/"Obsidian-Notes"

def test_testfile_validity():

    assert testHelpers.ValidateTestFiles() == True


def test_sha256_hash(testdata):

    assert testHelpers.sha256Hash(TEST_FOOTAGE_DIRECTORY / "Game 1/game1.mp4") == "b7f4e6b3b470003c099a4a5731d0e7ad160dcbda25e09c7d6ed6079afecbf352"

    with pytest.raises(FileNotFoundError):
        testHelpers.sha256Hash(TEST_FOOTAGE_DIRECTORY / "filethatshouldnotexist.gafh")

