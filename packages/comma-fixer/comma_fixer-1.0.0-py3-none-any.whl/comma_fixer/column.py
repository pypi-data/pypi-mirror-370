import re
from dataclasses import dataclass
from typing import Callable, Optional, TypeAlias

import numpy as np
import pandas as pd

IsValidFunction: TypeAlias = Callable[[str], bool]
"""
    TypeAlias for Callable[[str], bool]
"""
Ndtype: TypeAlias = type
"""
    TypeAlias for
"""


@dataclass
class Column:
    """
    Column class which contains information about a column's types and
    what elements can be inserted into the column.

    Attributes:
        _name (str): Name of column.
        _data_type (type): Column type.
        _nullable (bool): Whether elements in column can be null.
        _has_commas (bool): Whether elements in column can contain commas.
        _has_spaces (bool): Whether elements in column can contain spaces.
        _format (Optional[str]): RegEx formatting for elements in column if needed.
        _is_valid (IsValidFunction): Function used to check if an element can be placed in column.
    """

    _name: str
    _data_type: type
    _series_type: pd.Series
    _nullable: bool
    _has_commas: bool
    _has_spaces: bool
    _format: Optional[str]
    _is_valid: IsValidFunction

    @classmethod
    def new(
        cls,
        name: str,
        data_type: type,
        series_type: pd.Series,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str],
    ) -> "Column":
        """
        Creates a Column with supplied arguments and returns it.

        Args:
            name (str): Name of column.
            data_type (type): Column type.
            nullable (bool): Whether elements in column can be null.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for elements in column if needed.
            is_valid (IsValidFunction): Function used to check if an element can be placed in column.

        Returns:
            Column. Column object with specified values.
        """
        return Column(
            _name=name,
            _data_type=data_type,
            _series_type=series_type,
            _nullable=is_nullable,
            _has_commas=has_commas,
            _has_spaces=has_spaces,
            _format=format,
            _is_valid=Column.__create_is_valid_function(
                column_type=data_type,
                is_nullable=is_nullable,
                has_commas=has_commas,
                has_spaces=has_spaces,
                format=format,
            ),
        )

    @classmethod
    def string(
        cls,
        name: str,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str] = None,
    ) -> "Column":
        """
        Creates a Column of string type.

        Note that string types will be stored as
        objects in pandas.Series and pandas.DataFrame.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).

        Returns:
            Column of string type.
        """
        # Change the type here
        data_type = str
        series_type = pd.Series(dtype=object)

        # In the case of strings, use Object for pandas.Series type
        return Column.new(
            name=name,
            data_type=data_type,
            series_type=series_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

    @classmethod
    def numeric(
        cls,
        name: str,
        is_nullable: bool = False,
        has_commas: bool = False,
        has_spaces: bool = False,
        format: Optional[str] = None,
    ) -> "Column":
        """
        Creates a Column of numeric (integer) type.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).

        Returns:
            Column of numeric type.
        """
        # Change the type here
        data_type = int
        series_type = pd.Series(dtype=int)

        # In the case of strings, use Object for pandas.Series type
        return Column.new(
            name=name,
            data_type=data_type,
            series_type=series_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

    @classmethod
    def float(
        cls,
        name: str,
        is_nullable: bool = False,
        has_commas: bool = False,
        has_spaces: bool = False,
        format: Optional[str] = None,
    ) -> "Column":
        """
        Creates a Column of float type.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).

        Returns:
            Column with of type.
        """
        # Change the type here
        data_type = float
        series_type = pd.Series(dtype=float)

        # In the case of strings, use Object for pandas.Series type
        return Column.new(
            name=name,
            data_type=data_type,
            series_type=series_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

    @classmethod
    def datetime(
        cls,
        name: str,
        is_nullable: bool = False,
        has_commas: bool = False,
        has_spaces: bool = False,
        format: Optional[str] = None,
    ) -> "Column":
        """
        Creates a Column of datetime type.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).

        Returns:
            Column of Datetime type.
        """
        # Change the type here
        data_type = np.datetime64
        series_type = pd.Series(dtype="datetime64[ns]")

        # In the case of strings, use Object for pandas.Series type
        return Column.new(
            name=name,
            data_type=data_type,
            series_type=series_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

    @classmethod
    def __create_is_valid_function(
        cls,
        column_type: type,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str] = None,
    ) -> IsValidFunction:
        """
        Create a function to verify whether an element belongs within a column.

        Function is created based on the arguments passed in.

        Args:
            column_type (type): Python type or numpy.dtype of elements in column.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).

        Returns:
            Callable[[str], bool]. Function which takes in a string and returns
            whether the element belongs in a given column.
        """

        def is_valid(input: str) -> bool:
            if len(input) == 0:
                return is_nullable

            try:
                parsed_input = column_type(input)

                if column_type == str:
                    if " " in parsed_input and not has_spaces:
                        return False
                    if "," in parsed_input and not has_commas:
                        return False
                    if format is not None:
                        if re.match(format, parsed_input) is None:
                            return False
                return True
            except ValueError:
                return False

        return is_valid

    def get_name(self) -> str:
        """
        Returns column name.
        """
        return self._name

    def get_type(self) -> type:
        """
        Returns data type of column.
        """
        return self._data_type

    def get_series_type(self) -> pd.Series:
        """
        Returns pandas.Series type for initialising DataFrame.
        """
        return self._series_type

    def is_nullable(self) -> bool:
        """
        Returns whether elements in column can be null.
        """
        return self._nullable

    def has_commas(self) -> bool:
        """
        Returns whether elements in column can contain commas.
        """
        return self._has_commas

    def has_spaces(self) -> bool:
        """
        Returns whether elements in column can contain spaces.
        """
        return self._has_spaces

    def get_format(self) -> Optional[str]:
        """
        Returns RegEx formatting of elements in column if needed.
        """
        return self._format

    def is_valid(self, token: str) -> bool:
        """
        Returns whether elements can be placed in this column.
        """
        return self._is_valid(token)
