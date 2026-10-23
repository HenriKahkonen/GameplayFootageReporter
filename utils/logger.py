"""Module for a logger class that handles printing and writing to a .txt document"""

from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from utils.game_footage_data_classes import GameFootageSummary

@dataclass
class LoggedFootageAnalysisError:
    """Creates a timestamped non-fatal error instance that can be handled or printed later"""
    exc : Exception
    footage_folder : str
    timestamp : str

class FootageAnalysisLogger:
    """
    Creates a logger for the footage analysis that handles printing and writing to a log file.

    Params:
        log_directory: Directory that the files are written to
        filename: File name of the log file. If left empty, creates a log file with the current date
        dummy_logger: Disables log outputs to file and log file creation, still prints in python.
    """
    def __init__(
            self,
            log_dir: Path | str,
            file_name: str = "log.txt",
            dummy_logger: bool = False,
            ):
        """Creates a new logger object and log file with specified filename."""

        self.file_name = file_name

        self.file_name = Path(log_dir / self.file_name)

        self.operation_start_time: datetime = datetime.now()

        self.dummy_logger = dummy_logger

        self.error_log : list[LoggedFootageAnalysisError] = []
        self.games : list[GameFootageSummary] = []

        # Create the file
        if not self.dummy_logger:
            with open(self.file_name, mode="a", encoding="utf-8") as f:
                f.write("")

    def log(self, message: str) -> None:
        """Appends a new row to the log file."""
        print(message)
        if not self.dummy_logger:
            with open(self.file_name, mode="a", encoding="utf-8") as f:
                f.write(f"{message}\n")

    def log_with_timestamp(self, message: str) -> None:
        """Prints and logs timestamped message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        if not self.dummy_logger:
            with open(self.file_name, mode="a", encoding="utf-8") as f:
                f.write(f"{msg}\n")

    def log_nonfatal_error(
            self,
            error : Exception,
            footage_folder : Path | str,
            message : str = "") -> None:
        """Print and logs a non_fatal error and collects the error to the Logger's errors list.
        
        Params:
            error: 
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print_msg = f"⚠️ NON_FATAL ERROR [{timestamp}] [{str(footage_folder)}]: {error}\n   {message}"

        self.log(print_msg)
        self.error_log.append(LoggedFootageAnalysisError(error, footage_folder,timestamp))

    def commit_game_summary(
            self,
            game_summary: GameFootageSummary
            ) -> None:
        """Add the current game's summary to the logger's games list.
        """

        self.games.append(game_summary)

    def _calculate_totals_and_averages(
            self
            ) -> dict:
        """Takes the game footage summaries stored in the logger and
        calculates the totals and averages of all of the footage found."""

        games_count = len(self.games)

        if games_count == 0:
            return {}

        total_video_files = sum(g.video_files for g in self.games)
        total_non_video_files = sum(g.non_video_files for g in self.games),
        total_length_secs = sum(g.total_video_length_secs for g in self.games)
        total_size_mb = sum(g.total_video_size_in_mb for g in self.games)
        total_minutes = total_length_secs / 60

        all_extensions = set()
        for g in self.games:
            all_extensions.update(g.file_ext_list)

        totals = {
            "games_analyzed" : games_count,
            "obsidian_notes_found" : sum(g.obsidian_note_found for g in self.games),
            "video_files" : total_video_files,
            "non_video_files" : total_non_video_files,
            "total_video_length_seconds" : total_length_secs,
            "total_video_size_megabytes" : total_size_mb,
            "file_extensions" : sorted(all_extensions),
            "avg_video_files_per_game" : (
                total_video_files / games_count if games_count else 0.0
            ),
            "avg_non_video_files_per_game" : (
                total_non_video_files / games_count if games_count else 0.0
            ),
            "avg_clip_length_secs" : (
                total_length_secs / total_video_files if total_video_files else 0.0
            ),
            "avg_size_per_min" : (
                total_size_mb / total_minutes if total_minutes else 0.0 
            ),
        }

        return totals

    def begin_logging_session(self):
        """Creates a timestamp and a starting marker for the log file."""

        if not self.dummy_logger:
            with open(self.file_name, mode="a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write("*"*100
                        +f"\nNew footage analysis session at {timestamp}\n"
                        +"*"*100+"\n")

    def end_logging_session(self):
        """Writes a finishing string to the log file."""

        # Break duration into human-readable parts
        total_seconds = int((datetime.now()-self.operation_start_time).total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{days}d {hours}h {minutes}m {seconds}s"

        totals = self._calculate_totals_and_averages()

        ftg_hours, remainder = divmod(totals.get("total_video_length_seconds",0),3600)
        ftg_mins, ftg_secs = divmod(remainder, 60)

        msgs = [
            "*" * 100 + f"\nAnalysis finished! Scanned for {duration_str}.\n",
            (
                f"Analyzed {totals.get("games_analyzed",0)} games, "
                f"{totals.get("obsidian_notes_found",0)} of which had a matching Obsidian note."
            ),

            (
                f"Found {totals.get("video_files",0)} video clips and {totals.get("non_video_files",0)} other files. "
                f"A total of {ftg_hours} hours, {ftg_mins} minutes and {ftg_secs} seconds of footage was found, "
                f"collectively {totals.get("total_video_size_megabytes"),0} Mbs of video footage."
            ),

            f"Found the following non-ignored filetypes: {totals.get("file_extensions",[])}",

            (
                f"Average game footage folder contains {totals.get("avg_video_files_per_game",0):.1f} video clips "
                f"and {totals.get("avg_non_video_files_per_game",0):.1f} other files. "
                f"Average length of clips is {totals.get("avg_clip_length_secs",0):.1f} seconds "
                f"and average file size in megabytes per minute of footage is {totals.get("avg_size_per_min",0):.1f} Mb."
            ),
        ]

        for msg in msgs:
            self.log(msg)

        if self.error_log: # [] or [LoggedFootageAnalysisException]
            self.log("Encountered these non_fatal errors:")

            for e in self.error_log:
                self.log(f"⚠️ Exception [{e.timestamp}] [{e.footage_folder}] : {e.exc!r}")

    def end_logging_session_controlled_crash(self,exc:Exception):
        """End logging session in a controlled way if an uncaught exception fails the process."""

        self.log(f"💥 The following uncaught exception caused the script to fail: {exc.__class__} 💥{exc.message}")
        self.log("Attempting to wrap up the log...\n")
        self.end_logging_session()
