from __future__ import annotations

import logging

import pandas as pd
from pandas import DataFrame, NaT, Series

from vectice.models.resource.metadata.column_metadata import (
    DateStat,
)
from vectice.models.resource.metadata.df_wrapper_pandas_default import DataFrameDefaultPandasWrapper

_logger = logging.getLogger(__name__)


class PandasDFWrapper(DataFrameDefaultPandasWrapper[DataFrame]):
    def __init__(self, dataframe: DataFrame):
        super().__init__(dataframe)

    def __compute_date_column_statistics__(self, series: Series) -> DateStat:
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
        series = pd.to_datetime(series)
        min_date = series.min().isoformat()
        mean = series.mean().isoformat()
        median = series.median().isoformat()
        max_date = series.max().isoformat()
        missing = series.isnull().sum() / len(series)

        if NaT in list(series):  # pyright: ignore[reportUnnecessaryContains]
            _logger.warning(
                "NaT value/s were found in the dataframe. Check that all date value/s are valid to ensure consistent statistics."
            )

        return DateStat(
            missing=float(missing), minimum=str(min_date), mean=str(mean), median=str(median), maximum=str(max_date)
        )
