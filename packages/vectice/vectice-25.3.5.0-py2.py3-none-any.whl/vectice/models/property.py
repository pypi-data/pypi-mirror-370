from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Property:
    """Defines a property for a model or a dataset.

    Parameters:
        key: The key to identify the property.
        value: The value of the property.
        timestamp: The timestamp of the property. Corresponds to the
            property creation time if not explicitly passed.
        name: The name of the property.
    """

    key: str
    value: str
    timestamp: datetime | str = datetime.now(timezone.utc).isoformat()
    name: str | None = None

    def __post_init__(self):
        if not isinstance(self.value, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.value = str(self.value)

    def __repr__(self) -> str:
        return f"Property(key='{self.key}', value='{self.value}')"

    def key_val_dict(self) -> dict[str, str | int]:
        return {"key": self.key, "value": self.value}
