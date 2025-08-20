from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark import pandas as ps
    from pyspark.pandas.frame import DataFrame as PysparkPandasDF


class TimeSeries:
    def __init__(self):
        pass

    def __len__(self) -> int:
        return 0

    def max(self) -> datetime:
        return datetime.now()

    def min(self) -> datetime:
        return datetime.now()

    def to_frame(self) -> PysparkPandasDF:
        return PysparkPandasDF()


class Series:
    def __init__(self):
        pass

    def isnull(self) -> Series:
        return Series()

    def sum(self) -> int:
        return 0

    @property
    def index(self) -> ps.Index:
        return ps.Index([0])

    def astype(self, type: str) -> TimeSeries:
        return TimeSeries()
