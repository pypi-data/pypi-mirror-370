from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.autolog.asset_services.dataset_service import DatasetService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.models.resource.metadata.db_metadata import TableType

if TYPE_CHECKING:
    from pyspark.sql import DataFrame as SparkDF
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDF


class AutologPysparkService(DatasetService):
    def __init__(
        self,
        key: str,
        asset: SparkDF | SparkConnectDF,
        phase_name: str,
        raw_cells_data: list[str],
        capture_schema_only: bool,
        prefix: str | None = None,
    ):
        self._asset = asset
        self._key = key
        self._phase_name = phase_name
        self._prefix = prefix

        super().__init__(raw_cells_data=raw_cells_data, capture_schema_only=capture_schema_only)

    def get_asset(self):
        dataset = self._create_vectice_dataset(self._asset, self._phase_name, self._key, TableType.SPARK, self._prefix)

        return {
            "variable": self._key,
            "dataset": dataset,
            "asset_type": VecticeType.DATASET,
        }
