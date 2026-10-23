"""Module for scanning the metadata of video files with ffmpeg."""
import json
import subprocess
from pathlib import Path
from utils.game_footage_data_classes import FootageVideoFile

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
        footage_files : list[Path]
    ) -> {list[FootageVideoFile], list[Exception]}:
    """Inspect each video file in the submitted list and build a FootageVideoFile for it. Return a list 
    of FootageVideoFile objects and a list of errors raised when analyzing the clips."""

    clips: list[FootageVideoFile] = []
    errors: list[Exception] = []

    for path in footage_files:
        result : Exception | FootageVideoFile = probe_video_file(path)

        if isinstance(result,FootageVideoFile):
            clips.append(result)
        else:
            errors.append(result)

    return clips, errors

def probe_video_file(
        path: Path | str
    ) -> FootageVideoFile | Exception:
    """Try to get all of the video metadata. If an error is raised, 
    return the error instead of raising it."""
    try:
        length_secs = round(_probe_duration_secs(path))
        size_mb = path.stat().st_size / BYTES_PER_MB
        size_per_min = size_mb / (length_secs / 60) if length_secs else 0.0

        return FootageVideoFile(
                file_name=path.name,
                video_length_in_seconds=length_secs,
                file_size_in_mb=size_mb,
                file_extension=path.suffix.lower(),
                size_per_min_in_mb=size_per_min,
            )
    
    except Exception as exc:
        return exc