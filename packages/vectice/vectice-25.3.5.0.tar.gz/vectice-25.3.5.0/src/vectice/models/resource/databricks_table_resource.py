from __future__ import annotations

import datetime
import re
from typing import Any, Optional

from dateutil import parser

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.connect.session import SparkSession as SparkConnectSession

    spark_imported = True
except ImportError:
    spark_imported = False
    pass

from vectice.models.resource.base import Resource
from vectice.models.resource.databricks import DatabricksTableSparkConnectSessionSQL, DatabricksTableSparkSessionSQL
from vectice.models.resource.metadata.column_metadata import DBColumn
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.db_metadata import DBMetadata, MetadataDB
from vectice.models.resource.metadata.extra_metadata import ExtraMetadata

TDataFrameType = DataFrameType


class DatabricksTableResource(Resource):
    """Databricks tables resource reference wrapper.

    This resource wraps Databricks tables paths that you have stored in Databricks with optional metadata and versioning.
    You pass it as an argument of your Vectice Dataset wrapper before logging it to an iteration.


    ```python
    from vectice import DatabricksTableResource

    db_resource = DatabricksTableResource(
        spark_client=spark,
        paths="my_table",
    )
    ```

    NOTE: **Vectice does not store your actual dataset. Instead, it stores your dataset's metadata, which is information about your dataset.
    These details are captured by resources tailored to the specific environment in use, such as: local (FileResource), Bigquery, S3, GCS...**


    Known limitations :
        - Resource size won't be captured when passing a specific version. Example: my_table@v2.
    """

    _origin = "DATABRICKS_TABLE"

    def __init__(
        self,
        paths: str | list[str],
        dataframes: TDataFrameType | list[TDataFrameType] | None = None,
        spark_client: SparkSession | None = None,
        capture_schema_only: bool = False,
        columns_description: dict[str, str] | str | None = None,
    ):
        """Initialize a DatabricksTableResource resource.

        Parameters:
            paths: The paths to retrieve the tables. Should be either the table name, the location of the table or full path of the table for Spark Connect.
            dataframes (Optional): The dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats. (Support Pandas, Spark, H2O)
            spark_client (Optional): The spark session allowing vectice to capture the table metadata.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            columns_description (Optional): A dictionary or path to a csv file to map the column's name to a specific description. Dictionary should follow the format { "column_name": "Description", ... }

        """
        if spark_imported is False:
            raise ImportError("Pyspark is not installed.")
        super().__init__(
            paths=paths,
            dataframes=dataframes,
            capture_schema_only=capture_schema_only,
            columns_description=columns_description,
        )
        self._spark_client = spark_client
        if spark_client and isinstance(
            spark_client, SparkConnectSession  # pyright: ignore[reportPossiblyUnboundVariable]
        ):
            self._databricks_table_sql = DatabricksTableSparkConnectSessionSQL(spark_client=spark_client)
        elif spark_client is not None:
            self._databricks_table_sql = DatabricksTableSparkSessionSQL(spark_client=spark_client)
        else:
            self._databricks_table_sql = None

    def _fetch_data(self):
        tables: dict[str, tuple[dict | None, TDataFrameType | None]] = {}
        df_index = 0
        for path in self._paths:
            path_tables, new_df_index = self._fetch_table_data(index=df_index, path=path)
            tables.update(path_tables)
            df_index += new_df_index
        return tables

    def _fetch_table_data(
        self, index: int, path: str
    ) -> tuple[dict[str, tuple[dict | None, TDataFrameType | None]], int]:
        table_display_name = path
        has_at = re.search("@", path)
        has_version = re.search("@v", path)
        table_path = path.split("@")[0] if has_at else path

        dataframe = self._dataframes[index] if self._dataframes is not None and len(self._dataframes) > index else None

        if self._spark_client is None:
            return {table_display_name: (None, dataframe)}, 1

        if self._databricks_table_sql is None:
            raise ValueError("A spark_client of type `SparkSession` is required.")
        self._databricks_table_sql.table_path = table_path

        table_name = table_path.rpartition("/")[-1]
        self._databricks_table_sql.set_table_key(table_name)
        schema: list | None = None
        detail: dict = {
            "location": None,
            "createdAt": None,
            "format": None,
            "lastModified": None,
            "sizeInBytes": None,
        }

        location: str | None = None
        try:
            detail = self._databricks_table_sql.get_detail_as_dict()
            if has_at is not None or has_version is not None:
                detail["sizeInBytes"] = None

            location = detail["location"]
            if location is not None:
                table_path = location
        except Exception:  # Handle views
            rows = self._databricks_table_sql.get_rows()

            row_created = next(row for row in rows if row["col_name"] == "Created Time")
            detail["createdAt"] = row_created["data_type"]
            end_row = next(row for row in rows if row["col_name"] == "" and row["data_type"] == "")
            schema = rows[: rows.index(end_row)]

        if schema is None:
            schema = self._get_schema(self._spark_client, has_version, has_at, path, table_path)

        table_format = detail["format"]
        extra_metadata: list[ExtraMetadata] = [
            ExtraMetadata(key="format", value=table_format, display_name="Format"),
        ]

        information = self._get_table_information()
        if "Type" in information:
            extra_metadata.append(ExtraMetadata(key="type", value=information["Type"], display_name="Type"))
        if detail["sizeInBytes"] is None and "Statistics" in information and has_at is None and has_version is None:
            match_bytes = re.search(r"([0-9]{1,15})( bytes)", information["Statistics"])
            if match_bytes is not None:
                detail["sizeInBytes"] = int(match_bytes.group(1))

        if table_format == "delta":
            extra_metadata.extend(self._get_delta_table_history_extra_metadata(has_version, has_at, path))

        if dataframe is None:
            key_rows_table_name = path.rpartition("/")[-1]
            self._databricks_table_sql.set_rows_table_name(key_rows_table_name)
            detail["rowsNumber"] = self._databricks_table_sql.get_number_of_rows()

        return {
            table_display_name: ({"detail": detail, "schema": schema, "extra_metadata": extra_metadata}, dataframe)
        }, 1

    def _get_schema(
        self,
        spark_session: SparkSession,
        has_version: Optional[re.Match[str]],
        has_at: Optional[re.Match[str]],
        path: str,
        table_path: str,
    ):
        if has_version:
            table = spark_session.read.option("versionAsOf", path.split("@v")[1]).load(table_path)
        elif has_at:
            table = spark_session.read.option("timestampAsOf", path.split("@")[1]).load(table_path)
        else:
            if self._databricks_table_sql is None:
                raise ValueError("A spark_client of type `SparkSession` is required.")
            try:
                table = self._databricks_table_sql.read_table_path(table_path)
            except Exception:
                return self._databricks_table_sql.get_detail()

        return list(map(lambda row: {"col_name": row.name, "data_type": row.dataType.jsonValue()}, table.schema))

    def _get_table_information(self) -> dict:
        if self._databricks_table_sql is None:
            raise ValueError("A spark_client of type `SparkSession` is required.")
        df = self._databricks_table_sql.get_table_extended()
        df_collected = df.collect()
        if len(df_collected) == 0:
            return {}
        dict_df_table = df_collected[0].asDict()
        if "information" not in dict_df_table:
            return {}
        information: str = dict_df_table["information"]
        pairs = information.split("\n")
        result_dict = {}

        for pair in pairs:
            if ": " in pair:
                key, value = pair.split(": ")
                key = key.strip()
                value = value.strip()
                result_dict[key] = value

        return result_dict

    def _get_delta_table_history_extra_metadata(
        self,
        has_version: Optional[re.Match[str]],
        has_at: Optional[re.Match[str]],
        path: str,
    ) -> list[ExtraMetadata]:
        if self._databricks_table_sql is None:
            raise ValueError("A spark_client of type `SparkSession` is required.")
        history = self._databricks_table_sql.get_table_history()
        if has_version:
            history_v = path.split("@v")[1]
            history_row = next(row for row in history if row["version"] == int(history_v))
        elif has_at:
            history_v = path.split("@")[1]
            history_row = next(row for row in history if row["timestamp"] == parser.parse(history_v))
        else:
            history_row = history[0]

        version = history_row["version"]
        date_time = history_row["timestamp"]
        return [
            ExtraMetadata(key="version", value=f"v{version}", display_name="Version"),
            ExtraMetadata(key="timestamp", value=str(date_time.isoformat()), display_name="Timestamp"),
        ]

    def _build_metadata(self) -> DBMetadata:
        tables_metadata: dict[str, tuple[dict | None, TDataFrameType | None]] = self.data
        dbs: list[MetadataDB] = []
        for table_name, [table_metadata, dataframe] in tables_metadata.items():
            columns: list[DBColumn] | None = None
            size = None
            updated_date = None
            created_date = None
            rows_number = None
            uri = None
            if table_metadata is not None and self._spark_client is not None:
                columns = []
                detail = table_metadata["detail"]
                created_at = detail["createdAt"]
                last_modified = detail["lastModified"]
                size = detail["sizeInBytes"]
                uri = detail["location"]
                if "rowsNumber" in detail:
                    rows_number = detail["rowsNumber"]

                def get_iso_format_from_str_or_date(date_time: Any) -> str | None:
                    if date_time is not None:
                        if isinstance(date_time, str):
                            return parser.parse(date_time).isoformat()
                        elif isinstance(date_time, datetime.datetime):
                            return date_time.isoformat()
                    return None

                created_date = get_iso_format_from_str_or_date(created_at)
                updated_date = get_iso_format_from_str_or_date(last_modified)

                for row in table_metadata["schema"]:
                    columns.append(
                        DBColumn(
                            name=row["col_name"],
                            data_type=row["data_type"],
                        )
                    )

            dbs.append(
                MetadataDB(
                    name=table_name,
                    size=size,
                    rows_number=rows_number,
                    columns=columns,
                    created_date=created_date,
                    updated_date=updated_date,
                    uri=uri,
                    dataframe=dataframe,
                    extra_metadata=table_metadata["extra_metadata"] if table_metadata is not None else None,
                    display_name=table_name.rpartition("/")[-1],
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
            size=metadata_size,
            origin=self._origin,
            dbs=dbs,
        )
        return metadata
