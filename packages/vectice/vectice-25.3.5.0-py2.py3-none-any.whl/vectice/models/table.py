from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


class Table:
    """Table wraps a dataframe into a table format, to enable the logging of custom metadata within Vectice.

    This class formats metadata into a tabular structure, enabling the ability to log tables for documentation purposes.
    Once logged, this structured metadata is accessible within the Vectice app.

    NOTE: **IMPORTANT INFORMATION**
        Vectice stores the metadata in its original form, ensuring it remains unaltered without any processing or transformation.

    """

    def __init__(
        self,
        dataframe: DataFrame,
        name: str | None = None,
    ):
        """Wrap a Table.

        A Vectice Table is a wrapped pandas dataframe in a table format, which can then be logged to a Vectice iteration. (Maximum of 100 rows and 20 columns).

        Parameters:
            dataframe: The pandas dataframe to be wrapped as table.
            name: The name of the table for future reference.

        """
        self._name = name or f"table {datetime.now()}"
        self._dataframe = dataframe

    @property
    def name(self) -> str:
        """The table's name.

        Returns:
            The table name.
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Set the table's name.

        Parameters:
            name: The name of the table.
        """
        self._name = name

    @property
    def dataframe(self) -> DataFrame:
        """The table's data.

        Returns:
            dataframe: The pandas dataframe to be displayed as table.
        """
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: DataFrame):
        """Set the table's pandas dataframe.

        Parameters:
            dataframe: The pandas dataframe to be displayed as table.
        """
        self._dataframe = dataframe
