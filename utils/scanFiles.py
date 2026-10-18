import os

def GetFootageFolders(directory:str) -> list[str]:
    """Get the list of folders inside the root path in alphabetical order. Does not return absolute paths, only the folder names."""
    return sorted(os.listdir(directory))
