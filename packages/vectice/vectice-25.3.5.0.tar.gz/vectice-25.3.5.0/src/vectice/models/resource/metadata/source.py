from __future__ import annotations

import logging
from typing import Any, Dict

from pandas.core.frame import DataFrame as PandasDF

from vectice.models.resource.metadata.base import MetadataSettings
from vectice.models.resource.metadata.column_metadata import Column
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.df_wrapper_h2o_frame import H2OFrameWrapper
from vectice.models.resource.metadata.df_wrapper_pandas import PandasDFWrapper
from vectice.models.resource.metadata.df_wrapper_pyspark_pandas import PysparkPandasDFWrapper
from vectice.models.resource.metadata.df_wrapper_resource import DataFrameWrapper
from vectice.models.resource.metadata.df_wrapper_spark_df import SparkDFWrapper
from vectice.models.resource.metadata.extra_metadata import ExtraMetadata

_logger = logging.getLogger(__name__)

TDataFrameType = DataFrameType


class Source:
    def __init__(
        self,
        name: str,
        size: int | None = None,
        columns: list[Column] | None = None,
        updated_date: str | None = None,
        created_date: str | None = None,
        uri: str | None = None,
        dataframe: TDataFrameType | None = None,
        extra_metadata: list[ExtraMetadata] | None = None,
        display_name: str | None = None,
        capture_schema_only: bool = False,
    ):
        """Initialize a MetadataDB instance.

        Parameters:
            name: The name of the source.
            size: The size of the source.
            columns: The columns that compose the source.
            updated_date: The date of last update of the source.
            created_date: The date of creation of the source.
            uri: The uri of the source.
            dataframe (Optional): A dataframe allowing vectice to optionally compute more metadata about this resource such as columns stats, size, rows number and column numbers. (Support Pandas and Spark)
            extra_metadata (Optional): Extra metadata to be captured.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.

        """
        self.name = name
        self.display_name = display_name
        self.size = size
        self.columns = columns
        self.created_date = created_date
        self.updated_date = updated_date
        self.uri = uri
        self.extra_metadata = extra_metadata
        self._dataframe = dataframe
        self._wrapper: PandasDFWrapper | PysparkPandasDFWrapper | SparkDFWrapper | H2OFrameWrapper | None = None
        self._settings = MetadataSettings()
        self.capture_schema_only = capture_schema_only

        if isinstance(self._dataframe, PandasDF):
            self._wrapper = PandasDFWrapper(self._dataframe)
        elif isinstance(self._dataframe, DataFrameWrapper):
            _logger.warning(
                "WARNING: Custom wrappers are not supported yet, pass a Pandas or a Spark DataFrame to get statistics."
            )
        else:
            try:
                from pyspark.pandas.frame import DataFrame as PysparkPandasDF
                from pyspark.sql.dataframe import DataFrame as SparkDF

                if isinstance(self._dataframe, SparkDF):
                    self._wrapper = SparkDFWrapper(self._dataframe)
                elif isinstance(self._dataframe, PysparkPandasDF):
                    _logger.warning(
                        "WARNING: Pandas on Spark DataFrame is not supported yet, pass a Pandas or a Spark DataFrame to get statistics."
                    )
                else:
                    try:
                        from h2o import H2OFrame  # type: ignore[reportMissingImports]

                        if isinstance(self._dataframe, H2OFrame):
                            self._wrapper = H2OFrameWrapper(self._dataframe)
                    except ImportError:
                        pass
            except ImportError:
                pass

    def set_settings(self, settings: MetadataSettings):
        self._settings = settings

    def asdict(self) -> dict[str, Any]:
        size_info: Dict[str, int | float | None] = {}
        skipped_statistics = False
        minimum_rows_for_statistics = self._settings.minimum_rows_for_statistics
        sample_rows_for_statistics = self._settings.sample_rows_for_statistics
        maximum_columns_for_statistics = self._settings.maximum_columns_for_statistics
        if self._wrapper is not None:
            df_info = self._wrapper.get_size()
            if df_info.rows < minimum_rows_for_statistics:
                skipped_statistics = True
                _logger.warning(
                    f"Statistics are not captured if numbers of rows are below {minimum_rows_for_statistics}, to keep the data anonymous."
                )
            size_info = df_info.asdict()

        columns_list: list[Column] = self.columns if self.columns is not None else []
        columns_list = (
            self._wrapper.capture_columns(
                minimum_rows_for_statistics,
                sample_rows_for_statistics,
                maximum_columns_for_statistics,
                capture_schema_only=self.capture_schema_only,
            )
            if self._wrapper is not None
            else columns_list
        )
        columns_list_dict = [col.asdict() for col in columns_list]
        exm = self.extra_metadata
        return {
            **size_info,
            "size": self.size,
            "name": self.name,
            "updatedDate": self.updated_date,
            "createdDate": self.created_date,
            "uri": self.uri,
            "columns": columns_list_dict,
            "skippedStatistics": skipped_statistics,
            "extraMetadata": [metadata.to_dict() for metadata in exm] if exm is not None else None,  # type: ignore[attr-defined]
        }
