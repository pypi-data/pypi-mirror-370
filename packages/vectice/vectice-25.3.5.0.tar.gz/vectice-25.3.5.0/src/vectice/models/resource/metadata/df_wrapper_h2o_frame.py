from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Tuple

from vectice.models.resource.metadata.column_metadata import (
    BooleanStat,
    Column,
    ColumnCategoryType,
    DateStat,
    MostCommon,
    NumericalStat,
    Quantiles,
    Size,
    TextStat,
)
from vectice.models.resource.metadata.df_wrapper_resource import DataFrameWrapper
from vectice.utils.common_utils import safe_float, to_datetime_safe

if TYPE_CHECKING:
    from h2o import H2OFrame  # type: ignore[reportMissingImports]
    from pandas import DataFrame

try:
    from h2o import H2OFrame  # pyright: ignore[reportMissingImports]

    h2o_imported = True
except ImportError:
    h2o_imported = False

_logger = logging.getLogger(__name__)


class H2OFrameWrapper(DataFrameWrapper):
    def __init__(self, dataframe: H2OFrame):
        if h2o_imported is False:
            raise ImportError("H2O is not installed.")
        super().__init__(dataframe)

    def get_size(self) -> Size:
        """Get the size (rows and columns) of the H2O Frame."""
        self.rows: int = self.dataframe.nrows
        self.columns_numbers: int = self.dataframe.ncols
        return Size(rows=self.rows, columns=self.columns_numbers)

    def capture_column_schema(self) -> list[Column]:
        """Capture the schema of columns in the H2O Frame."""
        list_schema: list[Column] = []

        for col_name in self.dataframe.columns:
            col_type = self.dataframe.type(col_name)
            column_cat: ColumnCategoryType | None = None

            if col_type in ["int", "real"]:
                column_cat = ColumnCategoryType.NUMERICAL
                dtype = "numeric"
            elif col_type == "time":
                column_cat = ColumnCategoryType.DATE
                dtype = "datetime"
            elif col_type == "enum":
                levels = self.dataframe[col_name].levels()[0]
                if len(levels) == 2 and set(str(l).lower() for l in levels) <= {"true", "false", "0", "1", "yes", "no"}:
                    column_cat = ColumnCategoryType.BOOLEAN
                    dtype = "boolean"
                else:
                    column_cat = ColumnCategoryType.TEXT
                    dtype = "categorical"
            elif col_type == "string":
                column_cat = ColumnCategoryType.TEXT
                dtype = "string"
            else:
                column_cat = None
                dtype = str(col_type)

            list_schema.append(
                Column(
                    name=col_name,
                    data_type=dtype,
                    stats=None,
                    category_type=column_cat,
                )
            )

        return list_schema

    def capture_column_statistics(
        self,
        list_col_schema: list[Column],
        sample_rows_for_statistics: int,
        maximum_columns_for_statistics: int,
    ) -> list[Column]:
        """Capture statistics for columns in the H2O Frame."""
        columns: list[Column] = []
        result: Dict[str, BooleanStat | NumericalStat | TextStat | DateStat] = {}

        column_split_by_type = self.__get_list_column_split_by_type__(list_col_schema, maximum_columns_for_statistics)
        result_numerical, result_str, result_bool, result_date = self.__compute_h2o_stats__(
            column_split_by_type, sample_rows_for_statistics
        )
        result = {**result_numerical, **result_str, **result_bool, **result_date}

        for idx, col in enumerate(list_col_schema):
            if idx == maximum_columns_for_statistics:
                _logger.warning(
                    f"Statistics are only captured for the first {maximum_columns_for_statistics} columns of your dataframe."
                )

            stat = result.get(col.name) if idx < maximum_columns_for_statistics else None
            col.stats = stat
            columns.append(col)

        return columns

    def __compute_h2o_stats__(
        self, column_values: Dict[str, list], sample_rows_for_statistics: int
    ) -> Tuple[Dict[str, NumericalStat], Dict[str, TextStat], Dict[str, BooleanStat], Dict[str, DateStat]]:
        """Compute statistics for different column types."""
        result_numerical: Dict[str, NumericalStat] = {}
        result_str: Dict[str, TextStat] = {}
        result_bool: Dict[str, BooleanStat] = {}
        result_date: Dict[str, DateStat] = {}

        # Sample the frame if needed
        if sample_rows_for_statistics > 0 and sample_rows_for_statistics < self.dataframe.nrows:
            sampled_frame = self.dataframe.sample(n=sample_rows_for_statistics, seed=42)
        else:
            sampled_frame = self.dataframe

        if len(column_values["numerical"]) > 0:
            result_numerical = self.__compute_numeric_column_statistics__(sampled_frame, column_values["numerical"])

        if len(column_values["string"]) > 0:
            result_str = self.__compute_string_column_statistics__(sampled_frame, column_values["string"])

        if len(column_values["boolean"]) > 0:
            result_bool = self.__compute_boolean_column_statistics__(sampled_frame, column_values["boolean"])

        if len(column_values["date"]) > 0:
            result_date = self.__compute_date_column_statistics__(sampled_frame, column_values["date"])

        return result_numerical, result_str, result_bool, result_date

    def __get_list_column_split_by_type__(
        self, list_col_schema: list[Column], maximum_columns_for_statistics: int
    ) -> Dict[str, list]:
        """Split columns by their types."""
        column_split_by_type: Dict[str, list] = {"numerical": [], "string": [], "boolean": [], "date": []}

        for idx, col in enumerate(list_col_schema):
            if idx >= maximum_columns_for_statistics:
                break

            column_name = col.name
            if col.category_type == ColumnCategoryType.NUMERICAL:
                column_split_by_type["numerical"].append(column_name)
            elif col.category_type == ColumnCategoryType.DATE:
                column_split_by_type["date"].append(column_name)
            elif col.category_type == ColumnCategoryType.BOOLEAN:
                column_split_by_type["boolean"].append(column_name)
            elif col.category_type == ColumnCategoryType.TEXT:
                column_split_by_type["string"].append(column_name)

        return column_split_by_type

    def __compute_numeric_column_statistics__(self, frame: H2OFrame, columns: list[str]) -> Dict[str, NumericalStat]:
        """Compute statistics for numeric columns."""
        result_stats: Dict[str, NumericalStat] = {}

        for col in columns:
            col_data = frame[col]

            if not isinstance(col_data, H2OFrame):
                _logger.debug(f"Column {col} is not a valid H2OFrame. Skipping statistics computation.")
                continue
            # Basic statistics
            count = frame.nrows
            missing_count = col_data.isna().sum()
            missing_percentage = missing_count / count if count > 0 else 0.0  # pyright: ignore

            non_null_data = col_data[~col_data.isna()]
            mean, std_dev, min_val, max_val = None, None, None, None

            # Statistical measures
            if non_null_data.nrows > 0:  # pyright: ignore
                mean = non_null_data.mean()[0]  # pyright: ignore
                std_dev = non_null_data.sd()[0]  # pyright: ignore
                min_val = non_null_data.min()  # pyright: ignore
                max_val = non_null_data.max()  # pyright: ignore

            # Quantiles: returns a list of lists e.g [[0.25, 1.0], [0.5, 2.0], [0.75, 3.0]]
            quantiles = self.to_pandas(col_data.quantile([0.25, 0.5, 0.75]), header=False, use_pandas=False)
            q25 = quantiles[0][1]
            q50 = quantiles[1][1]
            q75 = quantiles[2][1]

            result_stats[col] = NumericalStat(
                mean=safe_float(mean),
                std_deviation=safe_float(std_dev),
                quantiles=Quantiles(
                    q_min=safe_float(min_val),
                    q25=safe_float(q25),
                    q50=safe_float(q50),
                    q75=safe_float(q75),
                    q_max=safe_float(max_val),
                ),
                missing=float(missing_percentage),
            )

        return result_stats

    def __compute_string_column_statistics__(self, frame: H2OFrame, columns: list[str]) -> Dict[str, TextStat]:
        """Compute statistics for string/categorical columns."""
        result_stats: Dict[str, TextStat] = {}

        for col in columns:
            col_data = frame[col]
            if not isinstance(col_data, H2OFrame):
                _logger.debug(f"Column {col} is not a valid H2OFrame. Skipping statistics computation.")
                continue

            count = frame.nrows
            missing_count = col_data.isna().sum()
            missing_percentage = missing_count / count if count > 0 else 0.0  # pyright: ignore
            unique_count = col_data.unique().nrows

            try:
                table_df = (
                    self.to_pandas(col_data.table()).sort_values("Count", ascending=False).head(3)  # pyright: ignore
                )
                most_commons = [MostCommon(str(row[col]), int(row["Count"]) / count) for _, row in table_df.iterrows()]
            except Exception as e:
                _logger.warning(f"Failed to compute most common values for column {col}: {e}")
                most_commons = []

            result_stats[col] = TextStat(
                unique=safe_float(unique_count),
                missing=float(missing_percentage),
                most_commons=most_commons,
            )

        return result_stats

    def __compute_boolean_column_statistics__(self, frame: H2OFrame, columns: list[str]) -> Dict[str, BooleanStat]:
        """Compute statistics for boolean columns."""
        result_stats: Dict[str, BooleanStat] = {}

        for col in columns:
            col_data = frame[col]
            if not isinstance(col_data, H2OFrame):
                _logger.debug(f"Column {col} is not a valid H2OFrame. Skipping statistics computation.")
                continue

            count = frame.nrows
            missing_count = col_data.isna().sum()
            missing_percentage = missing_count / count if count > 0 else 0.0  # type: ignore

            true_count = 0
            false_count = 0

            try:
                table_df = self.to_pandas(col_data.table())
                value_counts = {str(row[col]).strip().lower(): int(row["Count"]) for _, row in table_df.iterrows()}  # type: ignore

                for key, count in value_counts.items():
                    if key in {"true", "1", "yes"}:
                        true_count += count
                    elif key in {"false", "0", "no"}:
                        false_count += count

            except Exception as e:
                _logger.warning(f"Failed to compute value counts for column '{col}': {e}")
                continue

            total_non_missing = true_count + false_count
            true_pct = true_count / total_non_missing if total_non_missing else 0.0
            false_pct = false_count / total_non_missing if total_non_missing else 0.0

            result_stats[col] = BooleanStat(
                true=safe_float(true_pct),
                false=safe_float(false_pct),
                missing=safe_float(missing_percentage),
            )

        return result_stats

    def __compute_date_column_statistics__(self, frame: H2OFrame, columns: list[str]) -> Dict[str, DateStat]:
        """Compute statistics for date columns."""
        result_stats: Dict[str, DateStat] = {}

        for col in columns:
            col_data = frame[col]
            if not isinstance(col_data, H2OFrame):
                _logger.debug(f"Column {col} is not a valid H2OFrame. Skipping statistics computation.")
                continue
            count = frame.nrows
            missing_count = col_data.isna().sum()
            missing_percentage = missing_count / count if count > 0 else 0.0  # pyright: ignore

            col_data_numeric = col_data.asnumeric()
            non_null_numeric = col_data_numeric[~col_data.isna()]
            min_date = to_datetime_safe(non_null_numeric.min())  # pyright: ignore
            max_date = to_datetime_safe(non_null_numeric.max())  # pyright: ignore

            try:
                median_ts = self.to_pandas(col_data.quantile(0.5))[1][0]
                median_date = (
                    datetime.fromtimestamp(median_ts / 1000, timezone.utc) if median_ts else None  # pyright: ignore
                )
            except Exception:
                try:
                    timestamps = self.to_pandas(col_data)[col].dropna()  # pyright: ignore
                    median_ts = timestamps.median()
                    median_date = datetime.fromtimestamp(median_ts / 1000, timezone.utc)
                except Exception as e:
                    _logger.warning(f"Failed to compute median for column {col}: {e}")
                    median_date = None
            try:
                timestamps = self.to_pandas(col_data).iloc[:, 0].dropna()  # pyright: ignore
                mean_ts = timestamps.mean()
                mean_date = datetime.fromtimestamp(mean_ts / 1000, timezone.utc) if mean_ts else None
            except Exception as e:
                _logger.warning(f"Failed to compute mean for column {col}: {e}")
                mean_date = None

            result_stats[col] = DateStat(
                missing=float(missing_percentage),
                minimum=str(min_date) if min_date is not None else None,
                mean=str(mean_date) if mean_date else None,
                median=str(median_date) if median_date else None,
                maximum=str(max_date) if max_date is not None else None,
            )

        return result_stats

    @staticmethod
    def to_pandas(h2o_frame: H2OFrame, header: bool = True, use_pandas: bool = True) -> DataFrame:
        """Converts H2OFrame to Pandas with version-safe threading support."""
        import h2o  # pyright: ignore[reportMissingImports]

        version_str = h2o.__version__
        major, minor = map(int, version_str.split(".")[:2])

        kwargs = {"use_pandas": use_pandas, "header": header}
        if (major, minor) >= (3, 44):
            kwargs["use_multi_thread"] = True
        else:
            kwargs["use_single_thread"] = False

        try:
            return h2o_frame.as_data_frame(**kwargs)  # pyright: ignore
        except TypeError:
            return h2o_frame.as_data_frame(use_pandas=use_pandas)  # pyright: ignore
