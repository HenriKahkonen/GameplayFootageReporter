"""Module for scanning the metadata of video files with ffmpeg."""
import json
import subprocess
from pathlib import Path
from utils.game_footage_data_classes import FootageVideoFile
from utils.settings_loader import Settings
from utils.scan_files import parse_full_folder_name_data

def _probe_duration_secs(path: Path) -> int:
    """Return the video's duration in full seconds using ffprobe in a subprocess.
    Raises error on failure."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False # check done in code
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip() or 'unknown error'}")

    duration = json.loads(result.stdout).get("format", {}).get("duration")

    if duration is None:
        raise ValueError("ffprobe returned no duration (file may not be a valid video)")
    return int(float(duration))

BYTES_PER_MB = 1024 * 1024

def analyze_clips(
        footage_files : list[Path],
        settings : Settings,
    ) -> {list[FootageVideoFile], list[Exception]}:
    """Inspect each video file in the submitted list and build a FootageVideoFile for it. Return a list 
    of FootageVideoFile objects and a list of errors raised when analyzing the clips."""

    clips: list[FootageVideoFile] = []
    errors: list[Exception] = []

    for path in footage_files:
        result : Exception | FootageVideoFile = probe_video_file(path, settings)

        if isinstance(result,FootageVideoFile):
            clips.append(result)
        else:
            errors.append(result)

    return clips, errors

def split_footage_path(path: Path, footage_root: Path) -> tuple[str,str]:
    """Splits the footage path to the game root and the subroute and filename."""
    rel = path.relative_to(footage_root)
    if len(rel.parts) < 2:
        raise ValueError(f"{path} is not inside a game folder under {footage_root}")
    return rel.parts[0], Path(*rel.parts[1:]).as_posix()

def probe_video_file(
        path: Path | str,
        settings: Settings
    ) -> FootageVideoFile | Exception:
    """Try to get all of the video metadata. If an error is raised, 
    return the error instead of raising it."""
    try:
        game_name, file_name = split_footage_path(Path(path), Path(settings.GAMEPLAY_FOOTAGE_PATH))
        length_secs = round(_probe_duration_secs(path))
        size_mb = path.stat().st_size / BYTES_PER_MB
        size_per_min = size_mb / (length_secs / 60) if length_secs else 0.0
        game_name = parse_full_folder_name_data(game_name,settings)[0]
        return FootageVideoFile(
                file_name=file_name,
                game_name=game_name,
                video_length_in_seconds=length_secs,
                file_size_in_mb=round(size_mb,2),
                file_extension=path.suffix.lower(),
                size_per_min_in_mb=round(size_per_min,2),
            )

    except Exception as exc:
        return exc
