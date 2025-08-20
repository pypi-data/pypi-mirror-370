from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectice.models.resource.databricks.base import TableSparkSession

if TYPE_CHECKING:
    from pyspark.sql import SparkSession
    from pyspark.sql.dataframe import DataFrame


class DatabricksTableSparkConnectSessionSQL(TableSparkSession):
    def __init__(self, spark_client: SparkSession):
        super().__init__(spark_client=spark_client)

    def set_table_key(self, table_name: str) -> None:
        pass

    def set_rows_table_name(self, key_rows_table_name: str) -> None:
        pass

    def get_detail(self) -> list:
        return self._spark_client.sql(f"DESCRIBE {self.table_path}").collect()

    def get_detail_as_dict(self) -> dict[str, Any]:
        return self._spark_client.sql(f"DESCRIBE DETAIL {self.table_path}").collect()[0].asDict()

    def get_rows(self) -> list:
        return self._spark_client.sql(f"DESCRIBE EXTENDED {self.table_path}").collect()

    def get_number_of_rows(self) -> int:
        return self._spark_client.sql("SELECT COUNT(*) FROM {self.table_path}").collect()[0][0]

    def get_schema(self) -> list:
        return self._spark_client.sql(f"DESCRIBE {self.table_path}").collect()

    def read_table_path(self, table_name: str) -> DataFrame:
        return self._spark_client.read.table(self.table_path)  # type: ignore[reportArgumentType]

    def get_table_history(self) -> list:
        return self._spark_client.sql(f"DESCRIBE HISTORY {self.table_path}").collect()

    def get_table_extended(self) -> DataFrame:
        return self._spark_client.sql(f"SHOW TABLE EXTENDED LIKE '{self.table_path}'")
