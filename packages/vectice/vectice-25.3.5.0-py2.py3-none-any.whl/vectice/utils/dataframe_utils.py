from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Hashable

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.models.table import Table

_logger = logging.getLogger(__name__)


def repr_list_as_pd_dataframe(list_arg: list | dict) -> DataFrame:  # type: ignore
    try:
        import pandas as pd
    except Exception as err:
        raise ModuleNotFoundError("To use this method, please install pandas first") from err
    if isinstance(list_arg, dict) and list_arg.get("data"):
        return pd.DataFrame(list_arg["data"])
    return pd.DataFrame(list_arg)


def _convert_datetime_columns_to_str(dataframe: DataFrame) -> DataFrame:
    datetime_columns = dataframe.select_dtypes(include=["datetime"]).columns
    if len(datetime_columns) >= 1:
        dataframe[datetime_columns] = dataframe[datetime_columns].astype(str)
    return dataframe


def transform_table_to_metadata_dict(asset: Table) -> list[dict[Hashable, Any]]:
    dataframe_reset_index = _reset_index(asset.dataframe).fillna("NaN")
    dataframe_cleaned = _convert_datetime_columns_to_str(dataframe_reset_index)
    try:
        import pandas as pd

        # convert objects to strings so the dataframe is json serializable
        dataframe_cleaned[dataframe_cleaned.select_dtypes(["object"]).columns] = dataframe_cleaned.select_dtypes(
            ["object"]
        ).astype(pd.StringDtype())
    except Exception:
        pass
    row_count, col_count = dataframe_cleaned.shape
    max_row_count = 100
    if row_count > max_row_count:
        dataframe_cleaned = dataframe_cleaned.iloc[0:max_row_count, :]
        _logger.warning(
            f"Only first {max_row_count} rows were captured. For additional capacity, please contact your sales representative or email support@vectice.com"
        )
    max_col_count = 20
    if col_count > max_col_count:
        dataframe_cleaned = dataframe_cleaned.iloc[:, 0:max_col_count]
        _logger.warning(
            f"Only first {max_col_count} columns were captured. For additional capacity, please contact your sales representative or email support@vectice.com"
        )
    columns_content = dataframe_cleaned.to_dict("records")
    return columns_content


def _reset_index(df: DataFrame) -> DataFrame:
    if not df.index.equals(df.index.to_frame().reset_index(drop=True).index):
        return df.reset_index()
    else:
        return df
