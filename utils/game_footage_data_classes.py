"""Module for the game footage file and game summary classes"""

from dataclasses import dataclass, fields

@dataclass
class GameFootageSummary:
    """A collection of a game's footage's values."""
    game_name : str
    video_files : int
    non_video_files : int
    obsidian_note_found : bool
    total_video_size_in_mb : float
    total_video_length_secs : int
    video_avg_length_secs : float
    video_avg_size_per_min_in_mb : float
    file_ext_list: list[str]

@dataclass
class GameSummary(GameFootageSummary):
    """A collection of all of the data gathered from the game"""
    release_year : int
    platforms : list[str]
    categories : list[str]
    genres : list[str]
    rating : int | float | None
    playtime_mins : int | None
    game_series : str | None
    developers : list[str]
    publishers : list[str]
    md_size : float | None
    omd_found : bool = False

    @classmethod
    def from_footage_summary(
        cls,
        ftg_summary: GameFootageSummary,
        **extra_fields,
    ) -> "GameSummary":
        """Build a GameSummary from an existing GameFootageSummary 
        plus the extra fields."""

        base_values = {f.name: getattr(ftg_summary, f.name) for f in fields(GameFootageSummary)}
        return cls(**base_values, **extra_fields)        

@dataclass
class FootageVideoFile:
    """A data class for a single footage video"""
    file_name : str
    video_length_in_seconds : int
    file_size_in_mb : float
    file_extension : str
    size_per_min_in_mb : float

def create_game_footage_summary(
    game_name: str,
    footage_files: list[FootageVideoFile],
    non_video_files: int,
    obsidian_note_found: bool,
) -> GameFootageSummary:
    """Create a GameFootageSummary from a list of FootageVideoFile objects.

    Params:
        game_name: Name of the game the footage belongs to.
        footage_files: The analyzed video files for this game.
        non_video_files: Count of files that ffmpeg couldn't analyze
            (not videos) in the footage folder.
        obsidian_note_found: Whether an Obsidian note exists for the game.
    """
    video_count = len(footage_files)
    total_size_mb = sum(f.file_size_in_mb for f in footage_files)
    total_length_secs = sum(f.video_length_in_seconds for f in footage_files)

    avg_length_secs = total_length_secs / video_count if video_count else 0.0
    total_minutes = total_length_secs / 60
    avg_size_per_min_mb = total_size_mb / total_minutes if total_minutes else 0.0

    file_ext_list = sorted({f.file_extension.lower() for f in footage_files})

    return GameFootageSummary(
        game_name=game_name,
        video_files=video_count,
        non_video_files=non_video_files,
        obsidian_note_found=obsidian_note_found,
        total_video_size_in_mb=total_size_mb,
        total_video_length_secs=total_length_secs,
        video_avg_length_secs=avg_length_secs,
        video_avg_size_per_min_in_mb=avg_size_per_min_mb,
        file_ext_list = file_ext_list
    )
