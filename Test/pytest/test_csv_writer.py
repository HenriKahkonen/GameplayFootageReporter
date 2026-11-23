"""Tests regarding the outputs of the .csv writer module."""

import os
from pathlib import Path

from utils.scan_files import get_footage_folders, get_game_metadata, sort_footage_folder, get_file_extensions
from utils.ffmpeg_scanning import analyze_clips
from utils.game_footage_data_classes import create_game_footage_summary, GameSummary
from utils.csvwriter import FootageReportCSVWriter as CSVWriter

# footage_dir, settings, testdata and notes_dir fixtures are defined in conftest.py.

# settings is a fresh Settings object for each test, so the test can override values they are testing for

def test_csv_report_creates_succesfully(settings):

    csv_writer = CSVWriter(
        csv_dir = settings.OUTPUT_PATH,
        file_name = "footage_report.csv",
        csv_separator = settings.CSV_SEPARATOR, # default ";"
        csv_floats_with_comma = settings.CSV_FLOATS_WITH_COMMA,
        csv_list_separator = settings.CSV_LIST_SEPARATOR, # default "|"
        dummy_logger = not settings.CSV_OUTPUT
    )

    game_list_raw = get_footage_folders(settings.GAMEPLAY_FOOTAGE_PATH)

    for footage_folder_name in game_list_raw:

        game_footage_path = Path(settings.GAMEPLAY_FOOTAGE_PATH / footage_folder_name)
        game_metadata= get_game_metadata(game_footage_path, settings)[0]

        footage_files, other_files = sort_footage_folder(
            game_footage_path,
            settings.SUPPORTED_VIDEO_FILETYPES,
            settings.IGNORED_FILETYPES)

        footage_clips = analyze_clips(footage_files,settings)[0]

        ftg_summary = create_game_footage_summary(
            game_name=game_metadata["game_name"],
            footage_files=footage_clips,
            non_video_files=len(other_files),
            obsidian_note_found=game_metadata["omd_found"],
            other_extensions=get_file_extensions(other_files)
            )

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

        csv_writer.add_game_summary(game_summary)

    csv_writer.write_csv()

    assert os.path.exists(Path(Path(settings.OUTPUT_PATH) / "footage_report.csv"))


def test_csv_report_can_be_read_with_pandas(settings):

    csv_writer = CSVWriter(
        csv_dir = settings.OUTPUT_PATH,
        file_name = "footage_report_test_output.csv", # pre-existing csv report to check
        csv_separator = settings.CSV_SEPARATOR, # default ";"
        csv_floats_with_comma = settings.CSV_FLOATS_WITH_COMMA,
        csv_list_separator = settings.CSV_LIST_SEPARATOR, # default "|"
        dummy_logger = not settings.CSV_OUTPUT
    )

    assert os.path.exists(Path(Path(settings.OUTPUT_PATH) / "footage_report_test_output.csv"))
    df = csv_writer.load_csv()

    assert df.columns[0] == "game_name"
    assert df.columns[11] == "platforms"

    assert df.loc[0, "game_name"] == "Game 1"
    assert df.loc[1, "release_year"] == 2002

def test_csv_report_expected_columns_check(settings):

    csv_writer = CSVWriter(
        csv_dir = settings.OUTPUT_PATH,
        file_name = "footage_report_test_output.csv", # pre-existing csv report to check
        csv_separator = settings.CSV_SEPARATOR, # default ";"
        csv_floats_with_comma = settings.CSV_FLOATS_WITH_COMMA,
        csv_list_separator = settings.CSV_LIST_SEPARATOR, # default "|"
        dummy_logger = not settings.CSV_OUTPUT
    )

    assert os.path.exists(Path(Path(settings.OUTPUT_PATH) / "footage_report_test_output.csv"))
    df = csv_writer.load_csv(expected_columns=[
        "game_name",
        "release_year",
        "total_video_size_in_mb",
        "total_video_length_secs",
        "video_avg_length_secs",
        "video_avg_size_per_min_in_mb",
        "file_ext_list",
        "video_files",
        "non_video_files",
        "obsidian_note_found",
        "md_size",
        "platforms",
        "categories",
        "genres",
        "rating",
        "playtime_mins",
        "game_series",
        "developers",
        "publishers",
    ])

    assert df is not None

    df = csv_writer.load_csv(expected_columns=[
        "game_name",
        "release_year",
    ])

    assert df is None
