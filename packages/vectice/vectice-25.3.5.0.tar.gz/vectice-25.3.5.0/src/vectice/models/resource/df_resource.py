from __future__ import annotations

import logging

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata.base import DatasetSourceOrigin
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.db_metadata import DBMetadata, MetadataDB, TableType

_logger = logging.getLogger(__name__)

from pandas import DataFrame as PandasDataFrame

try:
    from pyspark.sql import DataFrame as SparkDataFrame
except ImportError:
    SparkDataFrame = None
try:
    from h2o.frame import H2OFrame  # pyright: ignore[reportMissingImports]
except:
    H2OFrame = None

TDataFrameType = DataFrameType


class DFResource(Resource):
    """Wrap in-memory DataFrames into a Dataset Resource for metadata extraction.

    This resource is intended for DataFrames that exist only in memory (e.g., Pandas, Spark, or H2O) and are not associated with external file paths or storage locations.
    It enables Vectice to extract schema and optional column-level statistics from these DataFrames, which can be logged as part of a Dataset version.

    Unlike other resource types (e.g., FileResource, S3Resource, BigQueryResource), `DFResource` does not carry path or source metadata—its sole purpose is to wrap raw DataFrames.

    You typically use it when your data is generated on-the-fly, transformed in-memory, or does not have an accessible source path.

    ```python
    from vectice import DFResource, Dataset

    my_df_resource = DFResource(dataframes=df)
    Dataset.clean(name = 'my_dataset', resource = my_df_resource)
    ```

    NOTE: **Vectice does not store your actual dataset. Instead, it stores your dataset's metadata, which is information about your dataset.
    These details are captured by resources tailored to the specific environment in use, such as: local (FileResource), Bigquery, S3, GCS...**
    """

    _origin = DatasetSourceOrigin.LOCAL.value

    def __init__(
        self,
        dataframes: TDataFrameType | list[TDataFrameType],
        capture_schema_only: bool = False,
        columns_description: dict[str, str] | None = None,
    ):
        """Initialize a Dataframe resource resource.

        Parameters:
            dataframes: The dataframes allowing vectice to compute metadata about this resource such as columns schema and optionally statistics. (Support Pandas, Spark, H2O)
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            columns_description (Optional): A dictionary or path to a csv file to map the column's name to a specific description. Dictionary should follow the format { "column_name": "Description", ... }
        """
        super().__init__(
            paths="",
            dataframes=dataframes,
            capture_schema_only=capture_schema_only,
            columns_description=columns_description,
        )
        first_df = dataframes[0] if isinstance(dataframes, list) else dataframes
        self._type = self._infer_type(first_df)

    def _infer_type(self, df: TDataFrameType) -> TableType:
        if isinstance(df, PandasDataFrame):
            return TableType.PANDAS
        elif SparkDataFrame is not None and isinstance(df, SparkDataFrame):
            return TableType.SPARK
        elif H2OFrame is not None and isinstance(df, H2OFrame):
            return TableType.H2O
        else:
            return TableType.UNKNOWN

    def _fetch_data(
        self,
    ) -> dict:
        return {}

    def _build_metadata(self) -> DBMetadata:
        dbs = []
        if self._dataframes:
            for dataframe in self._dataframes:
                dbs.append(
                    MetadataDB(
                        name="Dataframe",
                        uri="Dataframe",
                        dataframe=dataframe,
                        display_name="Dataframe",
                        capture_schema_only=self.capture_schema_only,
                        columns=[],
                        type=self._type,
                    )
                )

            metadata = DBMetadata(
                size=0,
                origin=self._origin,
                dbs=dbs,
            )
            return metadata
        raise ValueError("A dataframe is required.")
