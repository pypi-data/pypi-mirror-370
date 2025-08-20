from __future__ import annotations

from enum import Enum
from typing import Any

from vectice.api.json.json_type import TJSON


class VersionStrategy(Enum):
    """Enumeration of the supported version strategies."""

    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"


class ArtifactVersion(TJSON):
    def __init__(
        self,
        version_number: int | None = None,
        version_name: str | None = None,
        version_id: str | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        if version_number is not None:
            self["versionNumber"] = version_number
        if version_name is not None:
            self["versionName"] = version_name
        if version_id is not None:
            self["id"] = version_id

    @property
    def version_number(self) -> int | None:
        return self.get("versionNumber", None)

    @property
    def version_id(self) -> int | None:
        return self.get("id", None)

    @property
    def version_name(self) -> int | None:
        return self.get("versionName", None)
