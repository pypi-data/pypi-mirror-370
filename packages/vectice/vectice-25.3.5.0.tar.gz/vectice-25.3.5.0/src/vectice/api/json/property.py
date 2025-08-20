from __future__ import annotations

import inspect
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


class PropertyInput:
    def __init__(self, key: str, value: str | int | float, timestamp: datetime | str | None = None):
        self.key: str = key
        self.value: str | int | float = str(value)
        if timestamp is None:
            self.timestamp: str = datetime.now(timezone.utc).isoformat()
        else:
            self.timestamp = timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp)


@dataclass
class PropertyOutput:
    id: int
    dataSetVersionId: int
    key: str
    value: str
    timestamp: datetime
    name: str | None = None

    @classmethod
    def from_dict(cls, properties: Any):
        return cls(**{k: v for k, v in properties.items() if k in inspect.signature(cls).parameters})

    def as_dict(self):
        return asdict(self)


def create_properties_input(properties: dict[str, int | float | str]) -> list[PropertyInput]:
    if len(set(properties)) < len(properties):
        raise ValueError("You can not use the same key value pair more than once.")
    props: list[PropertyInput] = []
    for key, value in properties.items():
        _check_empty_property(key, value)
        props.append(PropertyInput(key, str(value)))
    return props


def _check_empty_property(key: str, value: str | int | float):
    if key.strip() == "" or (isinstance(value, str) and value.strip() == ""):
        raise ValueError("Property keys and values can't be empty.")
