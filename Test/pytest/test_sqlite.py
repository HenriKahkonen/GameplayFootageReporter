"""Tests regarding the sqlite class and operations."""

import os

from utils.ffmpeg_scanning import (
    split_footage_path,
    )

from utils.scan_files import (
    sort_footage_folder,
    )

def test_path_splitting(test_game_paths, settings):

    game_path = test_game_paths[7] # SNES - Game 6 (1996)
    footages, others = sort_footage_folder(
        game_path, 
        settings.SUPPORTED_VIDEO_FILETYPES,
        settings.IGNORED_FILETYPES
        )

    test_clip_path = game_path / "general clips" / "game6-1.mp4"

    # Check the correct files are found
    assert len(footages) == 2
    assert len(others) == 2
    assert os.path.exists(test_clip_path)

    game_name_from_path, rest = split_footage_path(test_clip_path, settings.GAMEPLAY_FOOTAGE_PATH)

    assert game_name_from_path == "SNES - Game 6 (1996)"
    assert rest == "general clips/game6-1.mp4"
