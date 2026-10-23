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
from utils.scan_files import (
    get_footage_folders,
    get_game_metadata,
    sort_footage_folder)
from utils.validate_files import (
    validate_footage_path,
    validate_obsidian_path,
    validate_output_path)
from utils.ffmpeg_scanning import analyze_clips
from utils.settings_loader import Settings
from utils.parse_script_arguments import parse_args
from utils.logger import FootageAnalysisLogger
from utils.errors import EmptyFootageDirectoryError
from utils.game_footage_data_classes import (
    create_game_footage_summary,
    GameSummary)

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

    logger = FootageAnalysisLogger(
        log_dir = settings.OUTPUT_PATH,
        file_name = "log.txt",
        dummy_logger = not settings.LOG_OUTPUT
    )


    logger.begin_logging_session()

    logger.log("Generating report from gameplay footage and note directories...\n")
    logger.log(f"Reading gameplay footage from '{settings.GAMEPLAY_FOOTAGE_PATH}'")
    if settings.SCAN_OBSIDIAN_DB:
        logger.log(f"Reading supplementary Obsidian note database from '{settings.OBSIDIAN_DB_PATH}'")
    logger.log(f"Writing analysis files to '{settings.OUTPUT_PATH}'.\n")

    try:
        game_list_raw = get_footage_folders(settings.GAMEPLAY_FOOTAGE_PATH)
    except EmptyFootageDirectoryError as e:
        logger.end_logging_session_controlled_crash(e)
        return 1

    logger.log(f"Found {len(game_list_raw)} game footage folders.\n")

    for footage_folder_name in game_list_raw:

        game_footage_path = Path(settings.GAMEPLAY_FOOTAGE_PATH / footage_folder_name)

        game_metadata, errors = get_game_metadata(game_footage_path, settings)

        for e in errors:
            logger.log_nonfatal_error(e,footage_folder=footage_folder_name)

        print(game_metadata)

        footage_files, other_files = sort_footage_folder(
            game_footage_path,
            settings.SUPPORTED_VIDEO_FILETYPES,
            settings.IGNORED_FILETYPES)

        footage_clips, errors = analyze_clips(footage_files)

        for e in errors:
            logger.log_nonfatal_error(e,footage_folder=footage_folder_name)

        ftg_summary = create_game_footage_summary(
            game_name=game_metadata["game_name"],
            footage_files=footage_clips,
            non_video_files=len(other_files),
            obsidian_note_found=game_metadata["omd_found"]
            )

        logger.commit_game_summary(ftg_summary)

        game_summary = GameSummary.from_footage_summary(
            ftg_summary,
            release_year=game_metadata["year"],
            platforms=game_metadata["platforms"],
            categories=game_metadata["categories"],
            genres=game_metadata["genres"],
            rating=game_metadata["rating"],
            playtime_mins=game_metadata["playtime_mins"],
            game_series=game_metadata["game_series"],
            developers=game_metadata["developers"],
            publishers=game_metadata["publishers"],
            md_size=game_metadata["md_size"],
        )

        #print(game_summary)

        # if csv print print to csv
        # if sqlite save to sqlite

        

        return 1


    # TODO: go from there

    return 1

if __name__ == "__main__":
    gameplay_footage_report_generator(sys.argv)
