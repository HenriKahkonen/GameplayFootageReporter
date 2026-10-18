from utils.scanFiles import (GetFootageFolders)

TEST_FOOTAGE_DIRECTORY = "./Test/Gameplay-Footage"

def test_get_footage_dirs():

    assert GetFootageFolders(TEST_FOOTAGE_DIRECTORY) == [
        "Game 1", 
        "Game 2 (2002)", 
        "Game 3 (1997)", 
        "N64 - Game 4 (1999)", 
        "NES - Game 5 (1982)", 
        "PS2 - Game 8 (2002)", 
        "PSZ - Game 7 (1998)", 
        "SNES - Game 6 (1996)"
    ]
