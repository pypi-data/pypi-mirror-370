from typing import Union

from pandas.core.frame import DataFrame as PandasDF

from vectice.models.resource.metadata.df_wrapper_resource import DataFrameWrapper

try:
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDF
    from pyspark.sql.dataframe import DataFrame as SparkDF

    try:
        from pyspark.pandas.frame import DataFrame as PysparkPandasDF

        DataFramePandasType = Union[PysparkPandasDF, PandasDF]  # type: ignore
    except Exception:
        DataFramePandasType = PandasDF  # type: ignore

    DataFrameTypeWithoutWrapper = Union[DataFramePandasType, SparkDF, SparkConnectDF]  # type: ignore
    DataFrameType = Union[DataFrameTypeWithoutWrapper, DataFrameWrapper]  # type: ignore

except ImportError:
    DataFramePandasType = PandasDF  # type: ignore
    DataFrameType = Union[DataFramePandasType, DataFrameWrapper]  # type: ignore


try:
    from h2o import H2OFrame  # type: ignore[reportMissingImports]

    DataFrameType = Union[DataFrameType, H2OFrame]  # type: ignore[reportMissingImports]
except ImportError:
    pass  # type: ignore

MIN_ROWS_CAPTURE_STATS = 100
ROWS_SAMPLE_CAPTURE_STATS = 400
MAX_COLUMNS_CAPTURE_STATS = 400
