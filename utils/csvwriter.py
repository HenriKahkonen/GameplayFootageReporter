"""Module for a csv writer class that handles writing the games metadata into a .csv file"""

from pathlib import Path
import os

import pandas as pd

from utils.errors import MalformedSettingsError
from utils.game_footage_data_classes import GameSummary

class FootageReportCSVWriter:
    """A CSV Writer that collects Game Summaries and writes them out to a CSV file.
    Game Summaries are collected as a list of dictionaries and written to a dataframe when outputting to a file.
    """

    def __init__(
        self,
        csv_dir,
        file_name: str = "footage_report.csv",
        csv_separator: str = ";",
        csv_floats_with_comma: bool = False,
        csv_list_separator: str = "|",
        dummy_logger: bool = False,
    ):
        self.dummy = dummy_logger
        if self.dummy:
            return

        # This should be caught when validating arguments in the main loop 
        # but in case this code gets moved around it gets rechecked here
        if csv_floats_with_comma and csv_separator == ",":
            raise MalformedSettingsError(
                'CSV_SEPARATOR cannot be "," when CSV_FLOATS_WITH_COMMA is True.'
            )

        self.output_path = Path(csv_dir) / file_name
        self.separator = csv_separator
        self.decimal = "," if csv_floats_with_comma else "."
        self.list_separator = csv_list_separator
        self._rows: list[dict] = []

    def add_game_summary(self, game_summary : GameSummary | dict) -> None:
        """Add a game summary dictionary or a GameSummary to the table. Does nothing if the writer is set to be a dummy."""
        if self.dummy:
            return

        row = game_summary.to_dict()
        # Flatten lists (platforms, genres, file_ext_list, ...) into plain strings separated by the csv_list_separator
        for key, value in row.items():
            if isinstance(value, (list, tuple, set)):
                row[key] = self.list_separator.join(str(v) for v in value)
        self._rows.append(row)

    def to_dataframe(self) -> pd.DataFrame:
        """Return the current table as a DataFrame (empty if dummy)."""
        if self.dummy:
            return pd.DataFrame()
        return pd.DataFrame(self._rows)

    def write_csv(self) -> Path | None:
        """Write the table to the output file. Returns the path, or None if
        dummy or there is nothing to write."""
        if self.dummy or not self._rows:
            return None

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_csv(
            self.output_path,
            sep=self.separator,
            decimal=self.decimal,
            index=False,
            encoding="utf-8-sig",
        )
        return self.output_path

    def load_csv(
        self,
        path=None,
        expected_columns: list[str] | tuple[str, ...] | None = None,
    ) -> pd.DataFrame | None:
        """Try to load a pre-existing .csv file and create a pandas dataframe from it.
        For testing and code-reusability purposes.

        Uses the separator and decimal character this writer was configured with.

        Args:
            path: Path to the csv file. Defaults to this writer's own output file.
            expected_columns: If given (e.g. GameSummary.COLUMN_ORDER), the file must
                contain exactly these columns in this order to count as valid.

        Returns:
            None : if dummy, path doesn't exist or it isn't a valid csv
            pd.DataFrame : if a valid csv is found
        """
        if self.dummy:
            return None

        path = Path(path) if path is not None else self.output_path

        if not os.path.exists(path) or not path.is_file():
            return None
        if path.stat().st_size == 0:
            return None

        try:
            df = pd.read_csv(
                path,
                sep=self.separator,
                decimal=self.decimal,
                encoding="utf-8-sig",  # matches write_csv, strips the BOM
            )
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError, OSError):
            return None

        if df.empty: # will be empty if contains only header row
            return None

        # 4) Must have the expected structure
        if expected_columns is not None:
            if list(df.columns) != list(expected_columns):
                return None
        elif len(df.columns) < 2:
            # Without expected_columns, a single column almost always means
            # the wrong separator was used.
            return None

        return df
