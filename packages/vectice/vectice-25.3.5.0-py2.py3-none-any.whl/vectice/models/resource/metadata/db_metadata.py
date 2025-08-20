from __future__ import annotations

from enum import Enum

from vectice.models.resource.metadata.base import (
    DatasetSourceType,
    DatasetSourceUsage,
    Metadata,
)
from vectice.models.resource.metadata.column_metadata import DBColumn
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.extra_metadata import ExtraMetadata
from vectice.models.resource.metadata.source import Source

TDataFrameType = DataFrameType


class TableType(Enum):
    """Enumeration that defines what the table type is."""

    PANDAS = "PANDAS"
    SPARK = "SPARK"
    H2O = "H2O"
    UNKNOWN = "UNKNOWN"


class DBMetadata(Metadata):
    """Class that describes metadata of dataset that comes from a database."""

    def __init__(
        self,
        dbs: list[MetadataDB],
        size: int | None,
        usage: DatasetSourceUsage | None = None,
        origin: str | None = None,
    ):
        """Initialize a DBMetadata instance.

        Parameters:
            dbs: The list of databases.
            size: The size of the metadata.
            usage: The usage of the metadata.
            origin: The origin of the metadata.
        """
        super().__init__(size=size, type=DatasetSourceType.DB, usage=usage, origin=origin)
        self.dbs = dbs

    def asdict(self) -> dict:
        for db in self.dbs:
            if self._settings is not None:  # pyright: ignore[reportUnnecessaryComparison]
                db.set_settings(self._settings)
        return {
            **super().asdict(),
            "dbs": [db.asdict() for db in self.dbs],
        }


class MetadataDB(Source):
    def __init__(
        self,
        name: str,
        columns: list[DBColumn] | None,
        rows_number: int | None = None,
        size: int | None = None,
        updated_date: str | None = None,
        created_date: str | None = None,
        uri: str | None = None,
        dataframe: TDataFrameType | None = None,
        extra_metadata: list[ExtraMetadata] | None = None,
        display_name: str | None = None,
        capture_schema_only: bool = False,
        type: TableType = TableType.UNKNOWN,
    ):
        """Initialize a MetadataDB instance.

        Parameters:
            name: The name of the table.
            columns: The columns that compose the table.
            rows_number: The number of row of the table.
            size: The size of the table.
            updated_date: The date of last update of the table.
            created_date: The creation date of the table.
            uri: The uri of the table.
            dataframe (Optional): A dataframe allowing vectice to optionally compute more metadata about this resource such as columns stats, size, rows number and column numbers. (Support Pandas and Spark)
            extra_metadata (Optional): Extra metadata to be captured.
            display_name (Optional): Name that will be shown in the Web App.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            type (Optional): The table type.
        """
        super().__init__(
            name=name,
            size=size,
            columns=list(columns) if columns is not None else None,
            updated_date=updated_date,
            created_date=created_date,
            uri=uri,
            dataframe=dataframe,
            extra_metadata=extra_metadata,
            display_name=display_name,
            capture_schema_only=capture_schema_only,
        )
        self.rows_number = rows_number
        self.type = type

    def asdict(self) -> dict:
        return {
            "rowsNumber": self.rows_number,
            "columnsNumber": len(self.columns) if self.columns is not None else None,
            "type": self.type.value,
            **super().asdict(),
            "tablename": self.display_name,
        }
