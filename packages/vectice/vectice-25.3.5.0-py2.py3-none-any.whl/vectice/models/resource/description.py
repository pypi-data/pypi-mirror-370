from __future__ import annotations

from enum import Enum


class DataDescription:
    """This class allows to describe a dataset and its columns."""

    def __init__(self, columns: list[DataDescriptionColumn], summary: str):
        """Initialize a data description.

        Parameters:
            columns: The described columns of the dataset.
            summary: A brief summary for the dataset.
        """
        self._columns = columns
        self._summary = summary

    @property
    def columns(self) -> list[DataDescriptionColumn]:
        """The columns description of the dataset.

        Returns:
            The columns description of the dataset.
        """
        return self._columns

    @columns.setter
    def columns(self, columns: list[DataDescriptionColumn]):
        """Set the columns description of the dataset.

        Parameters:
            columns: The columns description of the dataset.
        """
        self._columns = columns

    @property
    def summary(self) -> str:
        """Get the summary of the dataset.

        Returns:
            The summary.
        """
        return self._summary

    @summary.setter
    def summary(self, summary: str):
        """Set the summary of the dataset.

        Parameters:
            summary: The summary of the dataset.
        """
        self._summary = summary


class DataDescriptionColumn(dict):
    """Class used to describe dataset columns."""

    def __init__(self, column_name: str, column_description: str, column_data_type: ColumnDataType):
        """Initialize a data description column.

        Parameters:
            column_name: The name of the column.
            column_description: A brief description of the column.
            column_data_type: The type of data contained in the column.
        """
        super(DataDescriptionColumn, self).__init__()
        self.column_name = column_name
        self.column_description = column_description
        self.column_type = column_data_type


class ColumnDataType(Enum):
    # TODO: complete this list with other common data types
    OBJECT = "OBJECT"
    INT64 = "INT64"
    FLOAT64 = "FLOAT64"
    BOOL = "BOOL"
    DATETIME64 = "DATETIME64"
    TIMEDELTA = "TIMEDELTA"
    CATEGORY = "CATEGORY"
    OTHER = "OTHER"
