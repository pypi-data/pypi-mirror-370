from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Metric:
    """Define a metric for a model or a dataset.

    Parameters:
        key: The key to identify the metric.
        value: The value of the metric.
        timestamp: The timestamp of the metric. Corresponds to the
            metric creation time if not explicitly passed.
        name: The name of the metric.
    """

    key: str
    value: int | float
    timestamp: datetime | str = datetime.now(timezone.utc).isoformat()
    name: str | None = None

    def __post_init__(self):
        if not (
            isinstance(self.value, int) or isinstance(self.value, float)  # pyright: ignore[reportUnnecessaryIsInstance]
        ):
            raise TypeError(
                f"Metric '{self.key}' value must have type float or integer, not {type(self.value).__name__}."
            )

    def __repr__(self) -> str:
        return f"Metric(key='{self.key}', value={self.value})"

    def key_val_dict(self) -> dict[str, str | int | float]:
        return {"key": self.key, "value": self.value}
