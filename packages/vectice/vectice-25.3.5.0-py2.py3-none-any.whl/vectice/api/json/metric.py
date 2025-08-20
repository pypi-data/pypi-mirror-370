from __future__ import annotations

import inspect
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from vectice.api.json.json_type import TJSON


@dataclass
class MetricInput(TJSON):
    def __init__(self, key: str, value: float | int, timestamp: datetime | str | None = None):
        super().__init__()
        self.key: str = key
        self.value: float | int = value
        if timestamp is None:
            self.timestamp: str = datetime.now(timezone.utc).isoformat()
        else:
            self.timestamp = timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp


@dataclass
class MetricOutput:
    key: str
    value: float
    timestamp: datetime
    name: str | None = None
    id: int | None = None

    @classmethod
    def from_dict(cls, metrics: Any):
        return cls(**{k: v for k, v in metrics.items() if k in inspect.signature(cls).parameters})

    def as_dict(self):
        return asdict(self)
