from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectice.models.resource.databricks.base import TableSparkSession

if TYPE_CHECKING:
    from pyspark.sql import SparkSession
    from pyspark.sql.dataframe import DataFrame


class DatabricksTableSparkSessionSQL(TableSparkSession):
    def __init__(self, spark_client: SparkSession):
        super().__init__(spark_client=spark_client)

    def set_table_key(self, table_name: str) -> None:
        self._spark_client.sql(f"SET key_table_name={table_name}")

    def set_rows_table_name(self, key_rows_table_name: str) -> None:
        self._spark_client.sql(f"SET key_rows_table_name={key_rows_table_name}")

    def get_detail(self) -> list:
        return self._spark_client.sql("DESCRIBE `${key_table_name}`").collect()

    def get_detail_as_dict(self) -> dict[str, Any]:
        return self._spark_client.sql("DESCRIBE DETAIL `${key_table_name}`").collect()[0].asDict()

    def get_rows(self) -> list:
        return self._spark_client.sql("DESCRIBE EXTENDED `${key_table_name}`").collect()

    def get_number_of_rows(self) -> int:
        return self._spark_client.sql("SELECT COUNT(*) FROM ${key_rows_table_name}").collect()[0][0]

    def get_schema(self) -> list:
        return self._spark_client.sql("DESCRIBE `${key_table_name}`").collect()

    def read_table_path(self, table_name: str) -> DataFrame:
        return self._spark_client.read.load(table_name)

    def get_table_history(self) -> list:
        return self._spark_client.sql("DESCRIBE HISTORY `${key_table_name}`").collect()

    def get_table_extended(self) -> DataFrame:
        return self._spark_client.sql("SHOW TABLE EXTENDED LIKE '${key_table_name}'")
