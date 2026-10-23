"""Tests regarding getting data from files and folders."""

from utils.ffmpeg_scanning import (
    probe_video_file,
    _probe_duration_secs,
    analyze_clips,
    )
from utils.scan_files import (
    sort_footage_folder,
    get_game_metadata,
    get_file_extensions
)
from utils.game_footage_data_classes import (
    FootageVideoFile,
    create_game_footage_summary,
    GameSummary
)

def test_footage_folder_sort(test_game_paths, settings):

    footages, others = sort_footage_folder(
        test_game_paths[1],
        settings.SUPPORTED_VIDEO_FILETYPES,
        settings.IGNORED_FILETYPES
        )

    assert len(footages) == 1
    assert len(others) == 1

def test_footage_folder_sort_ignores_files(test_game_paths, settings):

    footages, others = sort_footage_folder(
        test_game_paths[4],
        settings.SUPPORTED_VIDEO_FILETYPES,
        [".ignr"]
        )

    assert len(footages) == 1
    assert len(others) == 1

def test_video_probe_returns_right_class(test_game_paths, settings):

    for gamepath in test_game_paths:
        sort = sort_footage_folder(
            gamepath,
            settings.SUPPORTED_VIDEO_FILETYPES,
            settings.IGNORED_FILETYPES
            )

        footages = sort[0]
        result = probe_video_file(footages[0])

        assert isinstance(result, FootageVideoFile)

def test_video_sort_finds_nested_directories(test_game_paths, settings):

    footages, others =  sort_footage_folder(
            test_game_paths[7], # SNES - Game 6 (1996)
            settings.SUPPORTED_VIDEO_FILETYPES,
            settings.IGNORED_FILETYPES
            )

    assert len(footages) == 2
    assert len(others) == 2

def test_video_duration_probe(footage_dir, settings):
    clip_1 = footage_dir / "Game 1" / "game1.mp4"
    clip_2 = footage_dir / "Game 3 (1997)" / "game3.MOV"

    assert _probe_duration_secs(clip_1) == 6
    assert _probe_duration_secs(clip_2) == 2

def test_analyze_clips(footage_dir, settings):

    clips = sort_footage_folder(
        footage_dir / "PSZ - Game 7 (1998)",
        settings.SUPPORTED_VIDEO_FILETYPES,
        settings.IGNORED_FILETYPES)

    ftg_file_objects, errors = analyze_clips(clips[0])

    assert len(ftg_file_objects) == 3
    assert not errors

def test_analyze_clips_details(footage_dir, settings):

    clips, others = sort_footage_folder(
        footage_dir / "PSZ - Game 7 (1998)",
        settings.SUPPORTED_VIDEO_FILETYPES,
        settings.IGNORED_FILETYPES)

    ftg_file_objects, errors = analyze_clips(clips)
    v = ftg_file_objects[0]

    assert not errors
    assert v.file_name == "game7-1.mp4"
    assert v.video_length_in_seconds == 6
    assert v.file_size_in_mb < 1
    assert v.file_extension == ".mp4"
    assert v.size_per_min_in_mb < 0.3

def test_game_footage_summary(footage_dir, settings):

    gamepath = footage_dir / "Game 2 (2002)"

    metadata, errors = get_game_metadata(gamepath, settings)

    clips, others = sort_footage_folder(
        gamepath,
        [".avi"],
        settings.IGNORED_FILETYPES)


    ftg_objects, errors = analyze_clips(clips)

    ftg_summary = create_game_footage_summary(
        game_name = metadata["game_name"],
        footage_files = ftg_objects,
        non_video_files = len(others),
        obsidian_note_found = metadata["omd_found"],
        other_extensions = get_file_extensions(others))

    assert not errors

    assert ftg_summary.game_name == "Game 2"
    assert ftg_summary.video_files == 1
    assert ftg_summary.non_video_files == 1
    assert ftg_summary.obsidian_note_found is True
    assert 0.15 > ftg_summary.total_video_size_in_mb > 0
    assert ftg_summary.total_video_length_secs == 24
    assert ftg_summary.video_avg_length_secs == 24
    assert ftg_summary.file_ext_list == [".avi",".lcc"]

def test_game_full_summary(footage_dir, settings):

    gamepath = footage_dir / "Game 2 (2002)"

    game_metadata, errors = get_game_metadata(gamepath, settings)

    clips, others = sort_footage_folder(
        gamepath,
        [".avi"],
        settings.IGNORED_FILETYPES)

    ftg_objects, errors = analyze_clips(clips)

    ftg_summary = create_game_footage_summary(
        game_name = game_metadata["game_name"],
        footage_files = ftg_objects,
        non_video_files = len(others),
        obsidian_note_found = game_metadata["omd_found"],
        other_extensions = get_file_extensions(others))

    assert not errors

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

    assert game_summary.game_name == "Game 2" # from footage_summary

    assert game_summary.genres == ["Räiskintä"]
    assert game_summary.playtime_mins == 317
    assert game_summary.rating == 2
