import os, decimal
decimal.getcontext().prec = 3
from utils.errors import (EnvReadError,InvalidPathError)
from pathlib import Path
from typing import Any

FORBIDDEN_PATHS = [
        "/", "/*",
    ]

def ValidateFootagePath(footage_path: str | None) -> Path:
    """Checks the passed footage path and returns the validated path. Raises appropriate errors if path is invalid."""

    if footage_path is None:
        if not os.path.exists(".env"):
            raise EnvReadError("Error when resolving footage path: Cannot find .env file in the project root. Check that you have a file named '.env' in the same root folder as the settings.py and main.py files. Refer to the '.env.example' file for file formatting.")

        else:
            raise EnvReadError("Cannot read gameplay footage path from .env. Check that you have a .env file where your gameplay footage folder is properly configured.")

    if footage_path in FORBIDDEN_PATHS:
        raise InvalidPathError(f"The footage path '{footage_path}' is not allowed.")   

    if not os.path.exists(footage_path):
        raise InvalidPathError(f"The path '{footage_path}' does not exist. Make sure the submitted path points to an existing footage folder.")

    return Path(footage_path)

def ValidateObsidianPath(obsidian_path: str | None, scan_obsidian: bool, initialize_obsidian: bool) -> {Path | None, bool}:
    """Checks the submitted obsidian path and raises appropriate errors if the Obsidian path is invalid but obsidian scannig is set to true."""

    if not scan_obsidian and not initialize_obsidian:
        return None
    
    if obsidian_path is None:
        if not os.path.exists(".env"): 
            raise EnvReadError("Can't read Obsidian Database folder from .env or from passed arguments, but SCAN_OBSIDIAN_DB has been set to True in settings.py. Check that you have an .env file where your Obsidian folder is properly configured.")
        
    if obsidian_path in FORBIDDEN_PATHS:
        raise InvalidPathError(f"The obsidian database path '{obsidian_path}' is not allowed.")
    
    if not os.path.exists(obsidian_path):

        if initialize_obsidian:
            try: 
                os.mkdir(obsidian_path)
            except PermissionError:
                print(f"Cannot initialize Obsidian game notes database at {obsidian_path} due to insufficient permissions. Check your Obsidian database directory or run the program with elevated permissions.")
                raise
        
        raise FileNotFoundError(f"The specified Obsidian database folder path {obsidian_path} does not exist, but SCAN_OBSIDIAN_DB has been set to True in settings.py. Either set SCAN_OBSIDIAN_DB to False or check that your Obsidian folder is properly configured.")
    
    return Path(obsidian_path)

def ValidateOutputPath(output_path: str | None, use_custom_output_path: bool, sysargv: list[Any]) -> Path:
    """Validate the output path and return the path the script will use."""

    if not use_custom_output_path:
        script_dir = Path(sysargv[0]).resolve().parent
        return script_dir / "Output"

    if output_path is None:
        if not os.path.exists(".env"): 
            raise EnvReadError("Can't read Output file Database folder from .env or from passed arguments. set to True in settings.py. Check that you have an .env file where your Output directory is properly configured.")

    if output_path in FORBIDDEN_PATHS:
        raise InvalidPathError(f"The Output path '{output_path}' is not allowed.")

    if not os.path.exists(output_path):
        try:
            os.mkdir(output_path)
        except PermissionError:
            print(f"The path {output_path} does not exist, and when trying to create it the script does not have appropriate permissions. Either check the output folder or grant the script elevated rights.")
            raise

    return Path(output_path)
