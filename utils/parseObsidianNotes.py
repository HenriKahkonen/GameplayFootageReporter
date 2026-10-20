import logging
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any
import os

import yaml

from utils.settingsLoader import Settings

log = logging.getLogger(__name__)



# [[Target]], [[Target|Alias]], [[Target#Heading]]  ->  Target
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]*)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def normalizeName(name: str) -> str:
    """Normalize a file/folder name for comparison (case and unicode form)."""
    return unicodedata.normalize("NFC", name).casefold().strip()


@lru_cache(maxsize=4)
def buildObsidianNoteIndex(obsidian_path: str) -> dict[str, Path]:
    """
    Walk the vault once and map normalized note names to their paths.
    Cached so scanning many folders doesn't re-walk the vault each time.
    Call _build_note_index.cache_clear() if the vault changes mid-run.
    """
    index: dict[str, Path] = {}
    for md_file in Path(obsidian_path).rglob("*.md"):
        key = normalizeName(md_file.stem)
        if key in index:
            log.warning("Duplicate Obsidian note name '%s': %s and %s (keeping first)",
                        md_file.stem, index[key], md_file)
            continue
        index[key] = md_file
    return index


def stripObsidianWikilinks(text: str) -> str:
    """Strips Obsidian wikilinks to just their text."""
    return _WIKILINK_RE.sub(lambda m: m.group(1), text).strip()


def _coerce_scalar(value: Any, target: type) -> Any:
    """Convert a single YAML value to the target type. Returns None if empty/invalid."""
    if isinstance(value, list):  # a list where a scalar is expected: take the first item
        value = value[0] if value else None
    if value is None:
        return None

    try:
        if target is str:
            text = stripObsidianWikilinks(str(value))
            return text or None

        if target in (int, float):
            if isinstance(value, str):
                value = stripObsidianWikilinks(value).replace(",", ".")  # "3,5" -> "3.5"
                if not value:
                    return None
            number = float(value)
            return int(number) if target is int else number

        return target(value)
    except (ValueError, TypeError):
        log.warning("Could not convert %r to %s", value, target.__name__)
        return None


def _coerce(value: Any, spec: Any) -> Any:
    """
    Convert a parsed YAML value according to the OBSIDIAN_HEADERS type spec.
    `spec` is either a type (int, float, str) or a one-item list like [str].
    """
    if isinstance(spec, list):
        item_type = spec[0]
        if value is None:
            return []
        items = value if isinstance(value, list) else [value]
        converted = (_coerce_scalar(item, item_type) for item in items)
        return [item for item in converted if item is not None]

    return _coerce_scalar(value, spec)

_FRONTMATTER_RE = re.compile(r"\A\ufeff?---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)

def getObsidianFrontmatter(note_path: Path) -> str | None:
    """ Try and read the frontmatter (or: headers) of the obsidian note at the specified path. Returns either the string of the frontmatter or None."""
    text = note_path.read_text(encoding="utf-8-sig")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        log.warning("No frontmatter found in %s", note_path)
        return None
    return match.group(1)

def readObsidianFrontmatter(note_path: Path) -> dict[str, Any] | None:
    """Return the note's YAML frontmatter as a dict, or None if missing/invalid."""
    frontmatter_raw_text = getObsidianFrontmatter(note_path)
    if frontmatter_raw_text is None:
        return None
    
    try:
        data = yaml.safe_load(frontmatter_raw_text)
    except yaml.YAMLError as e:
        log.warning("Invalid YAML frontmatter in %s: %s", note_path, e)
        return None
    return data if isinstance(data, dict) else None

def getFileSize(filePath: str | Path, rounded: bool = False, decimals: int = 2) -> float:
    """Takes a file path and returns the file's size in kiloBytes. Only returns file size of files, not folders."""
    path = Path(filePath)
    if not path.exists():
        raise FileNotFoundError(f"File '{path}' does not exist.")

    if not path.is_file():
        raise ValueError(f"The path '{path}' refers to a directory, not a file.")
    
    size_bytes = path.stat().st_size

    if rounded:
        return round(size_bytes / 1024, decimals)

    return size_bytes / 1024

def getObsidianNoteFileSize(filepath: str | Path) -> float | None:

    path = Path(filepath)
    path_extension = os.path.splitext(path)[-1].lower()
    
    if path_extension != ".md":
        return None

    try:
        size_in_kb = getFileSize(filepath)
        return size_in_kb
    except (ValueError, FileNotFoundError):
        pass

    return None

def parseObsidianNote(
    folderName: str | Path,
    settings: Settings,
    obsidian_path: str | Path,
) -> dict | None:
    """
    Try to match the folder name to a matching Obsidian markdown note. If a match
    is found, return Obsidian's metadata defined in settings as a dictionary.

    The note is matched by file name: folder "NES - Game 5 (1982)" matches a note
    called "NES - Game 5 (1982).md" anywhere under obsidian_path.

    Returns:
        None if scanning is disabled, no note matches, or the note has no valid
        frontmatter. Otherwise a dict with one key per entry in
        settings.OBSIDIAN_HEADERS plus the file size under md_file_size. Missing or empty values become None
        (or [] for list-type headers).

    Raises:
        FileNotFoundError: if obsidian_path doesn't exist.
    """
    if not settings.SCAN_OBSIDIAN_DB:
        return {}

    obsidian_path = Path(obsidian_path)
    if not obsidian_path.is_dir():
        raise FileNotFoundError(f"Obsidian path does not exist or is not a folder: {obsidian_path}")

    note_name = Path(folderName).name
    note_path = buildObsidianNoteIndex(str(obsidian_path)).get(normalizeName(note_name))
    if note_path is None:
        return None

    frontmatter = readObsidianFrontmatter(note_path)
    if frontmatter is None:
        return None

    # Get md file size or None if invalid or unavailable
    md_file_size = getObsidianNoteFileSize(note_path)

    result = {
        header: _coerce(frontmatter.get(header), spec)
        for header, spec in settings.OBSIDIAN_HEADERS.items()
    }
    result["md_file_size"] = md_file_size

    return result