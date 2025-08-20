from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import Column
    from pyspark.sql._typing import ColumnOrName  # pyright: ignore[reportPrivateUsage]


def expr(str: str) -> Column: ...


def avg(col: ColumnOrName) -> Column: ...
