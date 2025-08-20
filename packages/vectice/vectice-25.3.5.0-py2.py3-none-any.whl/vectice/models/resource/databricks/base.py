from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyspark.sql import SparkSession
    from pyspark.sql.dataframe import DataFrame


class TableSparkSession(metaclass=ABCMeta):
    """Base class for TableSparkSession."""

    @abstractmethod
    def __init__(
        self,
        spark_client: SparkSession,
    ):
        """Initialize a resource."""
        self._spark_client = spark_client
        self._table_path: str | None = None

    @property
    def table_path(self) -> str | None:
        """The session's table path.

        Returns:
            The session's table path.
        """
        return self._table_path

    @table_path.setter
    def table_path(self, value: str):
        """Set session's table path.

        Parameters:
            value: The session's table path to set.
        """
        self._table_path = value

    @abstractmethod
    def set_table_key(self, table_name: str) -> None:
        pass

    @abstractmethod
    def set_rows_table_name(self, key_rows_table_name: str) -> None:
        pass

    @abstractmethod
    def get_detail(self) -> list:
        pass

    @abstractmethod
    def get_detail_as_dict(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_rows(self) -> list:
        pass

    @abstractmethod
    def get_number_of_rows(self) -> int:
        pass

    @abstractmethod
    def get_schema(self) -> list:
        pass

    @abstractmethod
    def read_table_path(self, table_name: str) -> DataFrame:
        pass

    @abstractmethod
    def get_table_extended(self) -> DataFrame:
        pass

    @abstractmethod
    def get_table_history(self) -> list:
        pass
