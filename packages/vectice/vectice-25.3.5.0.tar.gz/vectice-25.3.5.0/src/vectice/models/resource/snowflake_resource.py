from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from typing_extensions import TypedDict

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata import DatasetSourceOrigin
from vectice.models.resource.metadata.column_metadata import DBColumn
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.db_metadata import DBMetadata, MetadataDB

if TYPE_CHECKING:
    from snowflake.snowpark import Session
    from snowflake.snowpark.types import StructType

    TDataFrameType = DataFrameType  # because otherwise pyright can't find DataFrameType's type
    TTable = TypedDict(
        "TTable",
        {
            "num_bytes": int,
            "rows_number": int,
            "created": datetime | None,
            "modified": datetime | None,
            "schema": StructType,
        },
    )


_logger = logging.getLogger(__name__)


class SnowflakeResource(Resource):
    """Snowflake tables resource reference wrapper.

    This resource wraps Snowflake tables paths that you have stored in Snowflake with optional metadata and versioning.
    You pass it as an argument of your Vectice Dataset wrapper before logging it to an iteration.


    ```python
    from vectice import SnowflakeResource

    connection_parameters = {
        ...
    }
    new_session = Session.builder.configs(connection_parameters).create()

    sf_resource = SnowflakeResource(
        snowflake_client=new_session,
        paths="SNOWFLAKE_SAMPLE_DATA.TPCH_SF10.PART",
    )
    ```

    NOTE: **Vectice does not store your actual dataset. Instead, it stores your dataset's metadata, which is information about your dataset.
    These details are captured by resources tailored to the specific environment in use, such as: local (FileResource), Bigquery, S3, GCS...**
    """

    _origin = DatasetSourceOrigin.SNOWFLAKE.value

    def __init__(
        self,
        paths: str | list[str],
        dataframes: TDataFrameType | list[TDataFrameType] | None = None,
        snowflake_client: Session | None = None,
        capture_schema_only: bool = False,
        columns_description: dict[str, str] | str | None = None,
    ):
        """Initialize a Snowflake resource.

        Parameters:
            paths: The paths of the resources to get.
            dataframes (Optional): The dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats. (Support Pandas, Spark, H2O)
            snowflake_client (Optional): The Snowflake client to retrieve table metadata.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            columns_description (Optional): A dictionary or path to a csv file to map the column's name to a specific description. Dictionary should follow the format { "column_name": "Description", ... }

        """
        super().__init__(
            paths=paths,
            dataframes=dataframes,
            capture_schema_only=capture_schema_only,
            columns_description=columns_description,
        )
        self.snowflake_client = snowflake_client

    def _fetch_data(self) -> dict[str, tuple[TTable | None, TDataFrameType | None]]:
        tables: dict[str, tuple[TTable | None, TDataFrameType | None]] = {}
        df_index = 0
        for path in self._paths:
            path_tables, new_df_index = self._fetch_path_data(index=df_index, path=path)
            tables.update(path_tables)
            df_index += new_df_index
        return tables

    def _fetch_path_data(
        self, index: int, path: str
    ) -> tuple[dict[str, tuple[TTable | None, TDataFrameType | None]], int]:
        return self._fetch_table_data(index=index, path=path), 1

    def _fetch_table_data(self, index: int, path: str) -> dict[str, tuple[TTable | None, TDataFrameType | None]]:
        dataframe: TDataFrameType | None = (
            self._dataframes[index] if self._dataframes is not None and len(self._dataframes) > index else None
        )
        if self.snowflake_client is None:
            return {path: (None, dataframe)}

        from snowflake.snowpark.exceptions import SnowparkClientException

        tb: TTable | None = None
        try:
            schema = []
            session = self.snowflake_client
            table = session.table(path)
            schema = table.schema
            table_schema: str = path.split(".")[1]
            table_name = path.rpartition(".")[-1]
            sql = "SELECT ROW_COUNT, BYTES, CREATED, LAST_ALTERED FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ? and TABLE_NAME = ?"
            crsr = session.sql(sql, params=[table_schema, table_name]).collect()
            for a, b, c, d in crsr:
                tb = {"num_bytes": b, "rows_number": a, "created": c, "modified": d, "schema": schema}
        except SnowparkClientException:
            _logger.warning(f"Failed to fetch data information for table {path}")
            pass

        return {path: (tb, dataframe)}

    def _build_metadata(self) -> DBMetadata:
        tables_metadata: dict[str, tuple[TTable | None, TDataFrameType | None]] = self.data
        dbs: list[MetadataDB] = []
        for table_path, [table_metadata, dataframe] in tables_metadata.items():
            columns: list[DBColumn] | None = None
            size = None
            rows_number = None
            updated_date = None
            created_date = None
            if table_metadata is not None:
                columns = []
                size = table_metadata["num_bytes"]
                rows_number = table_metadata["rows_number"]
                modified = table_metadata["modified"]
                updated_date = modified.isoformat() if modified is not None else None
                created = table_metadata["created"]
                created_date = created.isoformat() if created is not None else None
                for column in table_metadata["schema"]:
                    columns.append(
                        DBColumn(
                            name=column.name,
                            data_type=str(column.datatype),
                            is_unique=False,
                            nullable=column.nullable,
                            is_private_key=False,
                            is_foreign_key=False,
                        )
                    )

            dbs.append(
                MetadataDB(
                    name=table_path,
                    rows_number=rows_number,
                    size=size,
                    columns=columns,
                    created_date=created_date,
                    updated_date=updated_date,
                    uri=table_path,
                    dataframe=dataframe,
                    display_name=table_path.rpartition(".")[-1],
                    capture_schema_only=self.capture_schema_only,
                )
            )

        metadata_size = None
        for db in dbs:
            if db.size is not None:
                if metadata_size is None:
                    metadata_size = 0
                metadata_size += db.size

        metadata = DBMetadata(
            size=int(metadata_size) if metadata_size else None,
            origin=self._origin,
            dbs=dbs,
        )
        return metadata
