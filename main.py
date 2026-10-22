"""
Program that reads a folder of footage, as well as optionally
a Obsidian notes database to create a data report on how many,
how large and how long video files exist under each footage folder
as well as deduces the game metadata from the Obsidian notes database.
"""

import sys
#import time
from pathlib import Path

#import cv2 # pip install opencv-python
from utils.scan_files import (get_footage_folders, get_game_metadata)
from utils.validate_files import (
    validate_footage_path,
    validate_obsidian_path,
    validate_output_path)
from utils.settings_loader import Settings
from utils.parse_script_arguments import parse_args

from Test.pytest.conftest import (
    unpack_tests,
    validate_test_files,
    generate_test_file_validation_baseline,
    delete_test_files
)

def gameplay_footage_report_generator(argv: list[str]) -> int:
    """Main program loop.
        Params:
            argv: System arguments
    """

    args = parse_args(argv)

    print("\n"+"*"*56+"\n*** Gameplay footage and game notes report generator ***\n"+"*"*56+"\n")

    if args.calculate_test_file_hash_baseline:
        generate_test_file_validation_baseline()
        return 0

    if args.unpack_tests:
        print("Unpacking the test files from the .zip archive...")
        unpack_tests()
        print("Validating test files...")
        validate_test_files()
        print("Test data succesfully unpacked.")
        return 0

    if args.remove_test_files:
        print("Removing test files from ./Test/Testdata...")
        delete_test_files()
        print("Test data cleared.")
        return 0

    # Validate paths and arguments

    settings = Settings()

    # TODO: remove test paths
    settings.GAMEPLAY_FOOTAGE_PATH = (
        "/mnt/data/repos/GameplayFootageReporter/Test/Testdata/Gameplay-Footage"
        )
    settings.OBSIDIAN_DB_PATH = (
        "/mnt/data/repos/GameplayFootageReporter/Test/Testdata/Obsidian-Notes"
        )
    settings.OUTPUT_TO_CUSTOM_DIRECTORY = False

    try:

        footage_path_candidate = args.footage_path or settings.GAMEPLAY_FOOTAGE_PATH
        obsidian_path_candidate = args.obsidian_path or settings.OBSIDIAN_DB_PATH
        output_path_candidate = args.output_to or settings.CUSTOM_OUTPUT_PATH
        initialize_obsidian = args.initialize_obsidian

        settings.GAMEPLAY_FOOTAGE_PATH = validate_footage_path(
            footage_path = footage_path_candidate
            )
        settings.OBSIDIAN_DB_PATH = validate_obsidian_path(
            obsidian_path = obsidian_path_candidate,
            scan_obsidian = settings.SCAN_OBSIDIAN_DB,
            initialize_obsidian = initialize_obsidian
        )

        if initialize_obsidian:
            print("WIP not implemented yet")
            return 0

        settings.OUTPUT_PATH = validate_output_path(
            output_path = output_path_candidate,
            use_custom_output_path = settings.OUTPUT_TO_CUSTOM_DIRECTORY,
            sysargv = argv
        )

    except Exception as exc:
        raise SystemExit from exc

    print("Generating report from gameplay footage and note directories...\n")
    print(f"Reading gameplay footage from '{settings.GAMEPLAY_FOOTAGE_PATH}'")
    if settings.SCAN_OBSIDIAN_DB:
        print(f"Reading supplementary Obsidian note database from '{settings.OBSIDIAN_DB_PATH}'")
    print(f"Writing analysis files to '{settings.OUTPUT_PATH}'.\n")

    game_list_raw = get_footage_folders(settings.GAMEPLAY_FOOTAGE_PATH)
    if len(game_list_raw) == 0:
        print("There are no footage folders under your footage directory!")
        return 1
    print(f"Found {len(game_list_raw)} game footage folders.\n")

    for footage_folder_name in game_list_raw:

        game_footage_path = Path(settings.GAMEPLAY_FOOTAGE_PATH / footage_folder_name)

        game_metadata = get_game_metadata(game_footage_path, settings)

        print(game_metadata)


    # TODO: go from there

    return 1

if __name__ == "__main__":
    gameplay_footage_report_generator(sys.argv)
