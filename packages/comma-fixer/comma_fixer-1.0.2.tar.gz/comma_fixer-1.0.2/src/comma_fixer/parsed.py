import csv
import logging
from dataclasses import dataclass
from typing import TypeAlias

import pandas as pd

from comma_fixer.schema import Schema

InvalidEntry: TypeAlias = tuple[int, str]
ParsedEntry: TypeAlias = list[str]
logger = logging.getLogger("Parsed Logs")


@dataclass
class Parsed:
    """
    Parsed class produced from calling `fix_file` in Fixer.

    Attributes:
        _schema (Schema): Schema of dataset.
        _processed (str): CSV of dataset stored as a string.
        _invalid_line_numbers (list[InvalidEntry]): List of invalid entries containing line number and entry.
        _skip_first_line (bool): Whether the original CSV file had headers as the first row.
    """

    _schema: Schema
    _processed: str
    _invalid_entries: list[InvalidEntry]
    _skip_first_line: bool

    @classmethod
    def new(
        cls,
        schema: Schema,
        processed_csv: str,
        invalid_entries: list[InvalidEntry],
        skip_first_line: bool,
    ) -> "Parsed":
        """
        Creates an empty Parsed object with specified Schema.

        Args:
            schema (Schema): Schema of dataset.
            processed_csv (str): Processed CSV as a string.
            invalid_entries (list[InvalidEntry]): List of invalid entries with line index.
            skip_first_line (bool): Whether the first line was skipped in original input file.

        Returns:
            Parsed. Parsed object with specified schema.
        """
        return Parsed(
            _schema=schema,
            _processed=processed_csv,
            _invalid_entries=invalid_entries,
            _skip_first_line=skip_first_line,
        )

    def export_to_csv_best_effort(self, filepath: str):
        """
        Exports valid entries to CSV at specified filepath.

        Converts valid entries into DataFrame before exporting to CSV.
        """
        processed_to_csv = pd.DataFrame(self._schema.get_series_dict())
        for line_number, line in enumerate(self._processed.split("\n")):
            if self._skip_first_line:
                line_number += 1
            if (line_number, line) not in self._invalid_entries:
                parsed_csv = list(csv.reader([line]))[0]
                processed_to_csv.loc[len(processed_to_csv)] = parsed_csv
        logger.info(processed_to_csv.info())
        return processed_to_csv.to_csv(filepath, index=False)

    def print_all_invalid_entries(self):
        """
        Prints all the invalid entries with their line index respective to
        the original CSV file.
        """
        print("Index\tLine entry")
        for invalid_index, invalid_line in self._invalid_entries:
            print(f"{invalid_index}\t{invalid_line}")

    def invalid_entries_count(self) -> int:
        return len(self._invalid_entries)
