from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict

from vectice.utils.common_utils import convert_keys_to_camel_case


class ColumnCategoryType(Enum):
    """Enumeration of the column category types."""

    BOOLEAN = "BOOLEAN"
    NUMERICAL = "NUMERICAL"
    DATE = "DATE"
    TEXT = "TEXT"


@dataclass
class Quantiles:
    """Model a key-value pair of a quantiles of a numerical column.

    Parameters:
        q_min: min value
        q25: quantile 25%
        q50: median
        q75: quantile 75%
        q_max: max value
    """

    q_min: float | None
    q25: float | None
    q50: float | None
    q75: float | None
    q_max: float | None


@dataclass
class MostCommon:
    """Model a value-frequency pair of a most commun category in a column of dtypes str.

    Parameters:
        value: The key to identify the statistic.
        frequency: The value of the statistic.
    """

    value: str
    frequency: float


@dataclass
class NumericalStat:
    """Model a key-value pair of a column statistic for numerical.

    Parameters:
        missing: The percentage of missing value between O and 1
        mean: mean of the column
        std_deviation: standard deviation of the column
        quantiles: modelise a Quantiles object
    """

    missing: float
    mean: float | None
    std_deviation: float | None
    quantiles: Quantiles


@dataclass
class DateStat:
    """Model a key-value pair of date column statistic.

    Parameters:
        missing: The percentage of missing value between O and 1
        minimum: the first date
        mean: the average date
        median: the median date
        maximum: the last date
    """

    missing: float | None
    minimum: str | None
    mean: str | None
    median: str | None
    maximum: str | None


@dataclass
class TextStat:
    """Model a key-value pair of a column statistic.

    Parameters:
        missing: The percentage of missing value between O and 1
        unique: The value of the statistic.
        most_commons: a list of MostCommon objects with value-frequency
    """

    missing: float | None
    unique: float | None
    most_commons: list[MostCommon]


@dataclass
class BooleanStat:
    """Model a key-value pair of a column statistic.

    Parameters:
        missing: The percentage of missing value between O and 1
        true: The percentage of True value between O and 1
        false: The percentage of False value between O and 1
    """

    missing: float | None
    true: float | None
    false: float | None


class Size:
    """Model size info of a dataframe."""

    def __init__(self, rows: int, columns: int):
        """Initialize the metadata of the DataFrame.

        Parameters:
            rows  The number of rows.
            columns : The number of columns.
        """
        self.rows = rows
        self.columns = columns

    def asdict(self) -> Dict[str, int | float | None]:
        return {"rowsNumber": self.rows, "columnsNumber": self.columns}


class Column:
    """Model a column of a dataset."""

    def __init__(
        self,
        name: str,
        data_type: str,
        stats: BooleanStat | TextStat | NumericalStat | DateStat | None = None,
        category_type: ColumnCategoryType | None = None,
    ):
        """Initialize a column.

        Parameters:
            name: The name of the column.
            data_type: The type of the data contained in the column.
            stats: Additional statistics about the column.
            category_type: Column category type.
        """
        self.name = name
        self.data_type = data_type
        self.stats = stats
        self.category_type = category_type

    def asdict(self) -> Dict[str, Any]:
        obj = {"name": self.name, "dataType": self.data_type, "statistics": {}}
        if self.category_type:
            obj["categoryType"] = self.category_type.value
            category_value = self.category_type.value.lower()
            if self.stats is not None:
                obj["statistics"] = {category_value: convert_keys_to_camel_case(asdict(self.stats))}

        return obj


class DBColumn(Column):
    """Model a column of a dataset, like a database column."""

    def __init__(
        self,
        name: str,
        data_type: str,
        is_unique: bool | None = None,
        nullable: bool | None = None,
        is_private_key: bool | None = None,
        is_foreign_key: bool | None = None,
        stats: BooleanStat | TextStat | NumericalStat | DateStat | None = None,
    ):
        """Initialize a column.

        Parameters:
            name: The name of the column.
            data_type: The type of the data contained in the column.
            is_unique: If the column uniquely defines a record.
            nullable: If the column can contain null value.
            is_private_key: If the column uniquely defines a record,
                individually or with other columns (can be null).
            is_foreign_key: If the column refers to another one,
                individually or with other columns (cannot be null).
            stats: Additional statistics about the column.
        """
        super().__init__(name, data_type, stats)
        self.is_unique = is_unique
        self.nullable = nullable
        self.is_private_key = is_private_key
        self.is_foreign_key = is_foreign_key

    def asdict(self) -> dict:
        return {
            **super().asdict(),
            "isUnique": self.is_unique,
            "nullable": self.nullable,
            "isPK": self.is_private_key,
            "isFK": self.is_foreign_key,
        }
