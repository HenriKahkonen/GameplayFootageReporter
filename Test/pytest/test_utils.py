"""
Tests for miscellaneous utilities.
"""

import os
import pytest

from Test.pytest.conftest import sha256_hash

def test_sha256_hash(footage_dir):

    assert sha256_hash(
        footage_dir / "Game 1/game1.mp4"
        ) == "b7f4e6b3b470003c099a4a5731d0e7ad160dcbda25e09c7d6ed6079afecbf352"

    with pytest.raises(FileNotFoundError):
        sha256_hash(footage_dir / "filethatshouldnotexist.gafh")

def test_test_game_list(test_game_paths):
    """Test that the test game paths resolve correctly."""

    for path in test_game_paths:
        assert os.path.isdir(path)