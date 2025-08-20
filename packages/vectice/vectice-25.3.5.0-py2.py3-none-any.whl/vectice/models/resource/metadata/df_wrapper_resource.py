from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from vectice.models.resource.metadata.column_metadata import Column, Size

T = TypeVar("T")


class DataFrameWrapper(ABC, Generic[T]):
    """Base class for dataframe wrappers.

    Use DataFrameWrapper subclasses to assign wrap DataFrames to generate statistics  The
    Vectice library supports a handful of common cases.  Additional
    cases are generally easy to supply by deriving from this base
    class.  In particular, subclasses must override this class'
    abstact methods (`capture_column_statistics()`, `capture_column_schema()`, `get_size()`).
    """

    def __init__(self, dataframe: T):
        self.dataframe = dataframe
        self.rows: int = 0

    @abstractmethod
    def get_size(self) -> Size:
        # self.rows to calculate
        pass

    @abstractmethod
    def capture_column_schema(self) -> list[Column]:
        pass

    @abstractmethod
    def capture_column_statistics(
        self,
        list_col_schema: list[Column],
        sample_rows_for_statistics: int,
        maximum_columns_for_statistics: int,
    ) -> list[Column]:
        pass

    def capture_columns(
        self,
        minimum_rows_for_statistics: int,
        sample_rows_for_statistics: int,
        maximum_columns_for_statistics: int,
        capture_schema_only: bool,
    ) -> list[Column]:
        list_schema = self.capture_column_schema()
        if self.rows >= minimum_rows_for_statistics and capture_schema_only is False:
            list_col_with_stats = self.capture_column_statistics(
                list_schema, sample_rows_for_statistics, maximum_columns_for_statistics
            )
            return list_col_with_stats

        return list_schema
