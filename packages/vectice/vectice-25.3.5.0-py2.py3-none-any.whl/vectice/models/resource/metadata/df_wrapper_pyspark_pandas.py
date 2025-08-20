from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.pandas.frame import DataFrame as PysparkPandasDF

from datetime import datetime

from vectice.models.resource.metadata.column_metadata import (
    DateStat,
)
from vectice.models.resource.metadata.df_wrapper_pandas_default import DataFrameDefaultPandasWrapper
from vectice.models.resource.metadata.pyspark_pandas_dataframe_typing import Series

_logger = logging.getLogger(__name__)


try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import avg, expr

    spark_imported = True
except ImportError:
    spark_imported = False

    from vectice.models.resource.metadata.pyspark_typing import avg, expr

    pass


class PysparkPandasDFWrapper(DataFrameDefaultPandasWrapper):
    def __init__(self, dataframe: PysparkPandasDF):
        if spark_imported is False:
            raise ImportError("Pyspark is not installed.")
        super().__init__(dataframe)
        self.spark = SparkSession.builder.getOrCreate()  # type: ignore @see: https://github.com/microsoft/pylance-release/issues/4577

    def __compute_date_column_statistics__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, series: Series
    ) -> DateStat:
        """Parse a dataframe series and return statistics about it.

        The computed statistics are:
        - the first date
        - the mean
        - the median
        - the last date
        - the count missing value in %
        Parameters:
            series: The pandas series to get information from.

        Returns:
            A DateStat object containing the above statistics.
        """
        # Convert to datetime since mean is not supported for non datetime pandas object such as dbdates
        series_time = series.astype("datetime64[ns]")
        min_date = series_time.min().isoformat()
        max_date = series_time.max().isoformat()
        missing = series.isnull().sum() / len(series_time)

        _temp = series_time.to_frame().to_spark()
        col_name = _temp.columns[0]

        df = _temp.withColumn(col_name, _temp[col_name].cast("timestamp"))
        mean = datetime.isoformat(df.agg(avg(col_name).cast("timestamp").alias("avg_created_datetime")).collect()[0][0])

        df = _temp.withColumn(col_name, expr(f"UNIX_TIMESTAMP(`{col_name}`, 'yyyy-MM-dd')"))
        median = df.approxQuantile(col_name, [0.5], 0.0)[0]
        median_iso = datetime.strptime(
            self.spark.sql(f"SELECT from_unixtime({median!s}, 'yyyy-MM-dd')").collect()[0][0], "%Y-%m-%d"
        ).isoformat()
        return DateStat(
            missing=float(missing), minimum=str(min_date), mean=str(mean), median=str(median_iso), maximum=str(max_date)
        )
