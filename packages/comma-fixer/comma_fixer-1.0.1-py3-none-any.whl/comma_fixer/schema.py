from dataclasses import dataclass
from typing import Callable, TypeAlias

import pandas as pd

from comma_fixer.column import Column

ColumnName: TypeAlias = str
"""
    TypeAlias for string
"""
IsValidFunction: TypeAlias = Callable[[str], bool]
"""
    TypeAlias for Callable[[str], bool]
"""


@dataclass
class Schema:
    """
    Class containing information on a dataset's columns.

    Stores a dictionary of Column objects by column name, with
    each Column object storing information related to what elements
    can be inserted into that column.

    Attributes:
        columns (dict[ColumnName, Column]): Collection of Columns by column name.
        series_types (dict[ColumnName, type]): Collection of types by column name
        for initialising DataFrame.
    """

    columns: dict[ColumnName, Column]

    @classmethod
    def new(cls, columns: list[Column]) -> "Schema":
        """
        Create a new Schema object.

        Schema can be added to define the name and type of a column in the
        schema, and how to determine whether an element belongs to that column.

        Used in conjunction with the Fixer class.

        Returns:
            Empty Schema.
        """
        column_by_name = dict()
        for column in columns:
            column_by_name[column.get_name()] = column
        return Schema(column_by_name)

    def is_token_valid(self, token: str, column_name: str) -> bool:
        """
        Check whether a string token is valid for a specified column.

        Calls the specified column's `is_valid` function to check
        whether the element can be placed in that column.

        Args:
            token (str): String token to be validated
            column_name (str): Column the token is validated against

        Returns:
            bool. Returns True if the token can be placed within the
            specified column, False otherwise.
        """
        return self.columns[column_name].is_valid(token)

    def get_column_names(self) -> list[str]:
        """
        Return a list of column names in the schema.

        Returns:
            List[str]. List containing the name of the columns in the schema.
        """
        return list(self.columns.keys())

    def get_series_dict(self) -> dict[ColumnName, pd.Series]:
        """
        Returns a dictionary of each column as a pandas.Series by
        column name for initialising a pandas.DataFrame.

        Used when dataset is being exported to CSV.

        Returns:
            dict[ColumnName, pd.Series]. Dictionary of pandas.Series
        """
        dataframe_columns = dict()
        for column_name, column in self.columns.items():
            dataframe_columns[column_name] = column.get_series_type()
        return dataframe_columns

    def __str__(self) -> str:
        return f"{self.types}"

    def info(self):
        """
        Prints out information about the current schema.
        """
        schema_df = pd.DataFrame(
            columns=["name", "type", "nullable", "has commas", "has spaces", "format"]
        )
        for column_name, column in list(self.columns.items()):
            schema_df.loc[len(schema_df)] = [
                column_name,
                column.get_type().__name__,
                column.is_nullable(),
                column.has_commas(),
                column.has_spaces(),
                column.get_format(),
            ]
        return schema_df.style
