from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    from pyspark.sql import DataFrame as SparkDF

from vectice.models.resource.metadata.column_metadata import (
    BooleanStat,
    Column,
    ColumnCategoryType,
    DateStat,
    NumericalStat,
    Quantiles,
    Size,
    TextStat,
)
from vectice.models.resource.metadata.df_wrapper_resource import DataFrameWrapper
from vectice.utils.common_utils import safe_float

_logger = logging.getLogger(__name__)

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import avg, expr

    spark_imported = True
except ImportError:
    spark_imported = False

    from vectice.models.resource.metadata.pyspark_typing import avg, expr

    pass


class SparkDFWrapper(DataFrameWrapper):
    def __init__(self, dataframe: SparkDF):
        if spark_imported is False:
            raise ImportError("Pyspark is not installed.")
        super().__init__(dataframe)
        self.spark = SparkSession.builder.getOrCreate()  # type: ignore @see: https://github.com/microsoft/pylance-release/issues/4577

    def get_size(self) -> Size:
        self.rows: int = self.dataframe.count()
        self.columns_numbers: int = len(self.dataframe.columns)

        return Size(rows=self.rows, columns=self.columns_numbers)

    def capture_column_schema(self) -> list[Column]:
        column_cat: ColumnCategoryType | None = None
        list_schema: list[Column] = []

        for column, column_type in self.dataframe.dtypes:
            column = str(column)
            if column_type in ["tinyint", "smallint", "int", "bigint", "float", "double"] or "decimal" in column_type:
                column_cat = ColumnCategoryType.NUMERICAL
                dtype = str(column_type)
            elif column_type == "date" or column_type == "timestamp":
                column_cat = ColumnCategoryType.DATE
                dtype = str(column_type)
            elif column_type == "boolean":
                column_cat = ColumnCategoryType.BOOLEAN
                dtype = str(column_type)
            elif column_type in ["string", "char", "varchar"]:
                column_cat = ColumnCategoryType.TEXT
                dtype = str(column_type)
            else:
                column_cat = None
                dtype = str(column_type)

            list_schema.append(
                Column(
                    name=column,
                    data_type=dtype if dtype != "object" else "string",
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
        columns: list[Column] = []
        stat: BooleanStat | NumericalStat | TextStat | DateStat | None = None
        result: Dict[str, BooleanStat | NumericalStat | TextStat | DateStat] = {}

        column_split_by_type = self.__get_list_column_split_by_type__(list_col_schema, maximum_columns_for_statistics)
        result_numerical, result_str, result_bool, result_date = self.__compute_spark_stats__(
            column_split_by_type, sample_rows_for_statistics
        )
        result = {**result_numerical, **result_str, **result_bool, **result_date}
        for idx, col in enumerate(list_col_schema):
            if idx == maximum_columns_for_statistics:
                _logger.warning(
                    f"Statistics are only captured for the first {maximum_columns_for_statistics} columns of your dataframe."
                )
            if col.name in result and idx < maximum_columns_for_statistics:
                stat = result[col.name]
            else:
                stat = None

            col.stats = stat
            columns.append(col)
        return columns

    def __compute_spark_stats__(
        self, column_values: Dict[str, list], sample_rows_for_statistics: int
    ) -> Tuple[Dict[str, NumericalStat], Dict[str, TextStat], Dict[str, BooleanStat], Dict[str, DateStat]]:
        result_numerical: Dict[str, NumericalStat] = {}
        result_str: Dict[str, TextStat] = {}
        result_bool: Dict[str, BooleanStat] = {}
        result_date: Dict[str, DateStat] = {}

        # Sampling the DataFrame if needed
        total_rows = self.dataframe.count()
        if sample_rows_for_statistics > 0 and sample_rows_for_statistics < total_rows:
            fraction = sample_rows_for_statistics / total_rows
            sampled_dataframe = self.dataframe.sample(fraction=fraction, seed=42)
        else:
            sampled_dataframe = self.dataframe
        if len(column_values["numerical"]) > 0:
            result_numerical = self.__compute_numeric_column_statistics__(
                sampled_dataframe.select(column_values["numerical"])
            )
        if len(column_values["string"]) > 0:
            result_str = self.__compute_string_column_statistics__(sampled_dataframe.select(column_values["string"]))

        if len(column_values["boolean"]) > 0:
            result_bool = self.__compute_boolean_column_statistics__(sampled_dataframe.select(column_values["boolean"]))

        if len(column_values["date"]) > 0:
            result_date = self.__compute_date_column_statistics__(sampled_dataframe.select(column_values["date"]))
        return result_numerical, result_str, result_bool, result_date

    def __get_list_column_split_by_type__(
        self, list_col_schema: list[Column], maximum_columns_for_statistics: int
    ) -> Dict[str, list]:
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

    def __compute_boolean_column_statistics__(self, dataframe: SparkDF) -> Dict[str, BooleanStat]:
        columns = dataframe.columns
        result_stats: Dict[str, BooleanStat] = {}

        agg_exprs = [
            expr("COUNT(*)").alias("count"),
            *[expr(f"SUM(CASE WHEN `{col}` = True THEN 1 ELSE 0 END)").alias(f"{col}_true") for col in columns],
            *[expr(f"SUM(CASE WHEN `{col}` IS NULL THEN 1 ELSE 0 END)").alias(f"{col}_missing") for col in columns],
            *[expr(f"SUM(CASE WHEN `{col}` = False THEN 1 ELSE 0 END)").alias(f"{col}_false") for col in columns],
        ]

        agg_results = dataframe.agg(*agg_exprs).collect()[0]

        for col in columns:
            count = agg_results["count"]
            true_count = agg_results[f"{col}_true"]
            false_count = agg_results[f"{col}_false"]
            missing_count = agg_results[f"{col}_missing"]

            true_percentage = true_count / count if count > 0 else 0.0
            false_percentage = false_count / count if count > 0 else 0.0
            missing_percentage = missing_count / count if count > 0 and missing_count is not None else 0.0

            result_stats[col] = BooleanStat(
                true=safe_float(true_percentage), false=safe_float(false_percentage), missing=float(missing_percentage)
            )

        return result_stats

    def __compute_numeric_column_statistics__(self, dataframe: SparkDF) -> Dict[str, NumericalStat]:
        columns = dataframe.columns
        result_stats: Dict[str, NumericalStat] = {}

        agg_exprs = [
            expr("COUNT(*)").alias("count"),
            *[expr(f"SUM(CASE WHEN `{col}` IS NULL THEN 1 ELSE 0 END)").alias(f"{col}_missing") for col in columns],
            *[expr(f"AVG(`{col}`)").alias(f"{col}_mean") for col in columns],
            *[expr(f"STDDEV(`{col}`)").alias(f"{col}_stddev") for col in columns],
            *[expr(f"MIN(`{col}`)").alias(f"{col}_min") for col in columns],
            *[expr(f"APPROX_PERCENTILE(`{col}`, 0.25)").alias(f"{col}_q25") for col in columns],
            *[expr(f"APPROX_PERCENTILE(`{col}`, 0.5)").alias(f"{col}_q50") for col in columns],
            *[expr(f"APPROX_PERCENTILE(`{col}`, 0.75)").alias(f"{col}_q75") for col in columns],
            *[expr(f"MAX(`{col}`)").alias(f"{col}_max") for col in columns],
        ]

        agg_results = dataframe.agg(*agg_exprs).collect()[0]
        result_stats = {}

        for col in columns:
            count = agg_results["count"]
            missing_count = agg_results[f"{col}_missing"]
            missing_percentage = missing_count / count if count > 0 and missing_count is not None else 0.0

            mean = agg_results[f"{col}_mean"]
            std_deviation = agg_results[f"{col}_stddev"]
            min_value = agg_results[f"{col}_min"]
            q25 = agg_results[f"{col}_q25"]
            q50 = agg_results[f"{col}_q50"]
            q75 = agg_results[f"{col}_q75"]
            max_value = agg_results[f"{col}_max"]

            result_stats[col] = NumericalStat(
                mean=safe_float(mean),
                std_deviation=safe_float(std_deviation),
                quantiles=Quantiles(
                    q_min=safe_float(min_value),
                    q25=safe_float(q25),
                    q50=safe_float(q50),
                    q75=safe_float(q75),
                    q_max=safe_float(max_value),
                ),
                missing=float(missing_percentage),
            )

        return result_stats

    def __compute_string_column_statistics__(self, dataframe: SparkDF) -> Dict[str, TextStat]:
        columns = dataframe.columns
        result_stats: Dict[str, TextStat] = {}
        agg_exprs = [
            expr("COUNT(*)").alias("count"),
            *[expr(f"SUM(CASE WHEN `{col}` IS NULL THEN 1 ELSE 0 END)").alias(f"{col}_missing") for col in columns],
            *[expr(f"APPROX_COUNT_DISTINCT(`{col}`)").alias(f"{col}_unique") for col in columns],
        ]

        agg_results = dataframe.agg(*agg_exprs).collect()[0]
        result_stats = {}

        for col_name in columns:
            count = agg_results["count"]
            missing_count = agg_results[f"{col_name}_missing"]
            missing_percentage = missing_count / count if count > 0 and missing_count is not None else 0.0

            unique_count = agg_results[f"{col_name}_unique"]

            result_stats[col_name] = TextStat(
                unique=safe_float(unique_count),
                missing=float(missing_percentage),
                most_commons=[],
            )

        return result_stats

    def __compute_date_column_statistics__(self, dataframe: SparkDF) -> Dict[str, DateStat]:
        columns = dataframe.columns
        result_stats: Dict[str, DateStat] = {}

        agg_exprs = [
            expr("COUNT(*)").alias("count"),
            *[expr(f"SUM(CASE WHEN `{col}` IS NULL THEN 1 ELSE 0 END)").alias(f"{col}_missing") for col in columns],
            *[expr(f"MIN(`{col}`)").alias(f"{col}_min") for col in columns],
            *[expr(f"MAX(`{col}`)").alias(f"{col}_max") for col in columns],
            *[avg(expr(f"UNIX_TIMESTAMP(`{col}`, 'yyyy-MM-dd')")).alias(f"{col}_mean") for col in columns],
            *[
                expr(f"APPROX_PERCENTILE(UNIX_TIMESTAMP(`{col}`, 'yyyy-MM-dd'), 0.25, 1000)").alias(f"{col}_median")
                for col in columns
            ],
        ]

        agg_results = dataframe.agg(*agg_exprs).collect()[0]

        for col in columns:
            count = agg_results["count"]
            missing_count = agg_results[f"{col}_missing"]
            missing_percentage = missing_count / count if count > 0 and missing_count is not None else 0.0

            min_date = agg_results[f"{col}_min"]
            max_date = agg_results[f"{col}_max"]
            mean_ts = agg_results[f"{col}_mean"]
            median_ts = agg_results[f"{col}_median"]

            mean_date = (
                datetime.fromtimestamp(int(agg_results[f"{col}_mean"]), timezone.utc) if mean_ts is not None else None
            )
            median_date = (
                datetime.fromtimestamp(int(agg_results[f"{col}_median"]), timezone.utc)
                if median_ts is not None
                else None
            )

            result_stats[col] = DateStat(
                missing=float(missing_percentage),
                minimum=str(min_date),
                mean=str(mean_date),
                median=str(median_date),
                maximum=str(max_date),
            )

        return result_stats
