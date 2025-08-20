from __future__ import annotations

from typing import Any

from vectice.api.json.json_type import TJSON
from vectice.models.resource.metadata.base import DatasetSourceType, DatasetSourceUsage


class DatasetResourceRepresentationOutput(TJSON):
    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def type(self) -> DatasetSourceType:
        return DatasetSourceType(self["type"])

    @property
    def usage(self) -> str:
        return DatasetSourceUsage(self["usage"]).value if self["usage"] else "GENERIC"

    @property
    def path(self) -> str:
        return str(self["uri"])

    @property
    def size(self) -> int | None:
        return int(self["size"]) if self["size"] else None

    @property
    def name(self) -> str:
        return self["filename"] if "filename" in self else self["tablename"]

    @property
    def columns_count(self) -> int | None:
        return int(self["columnsNumber"]) if self["columnsNumber"] else None

    @property
    def rows_count(self) -> int | None:
        return int(self["rowsNumber"]) if self["rowsNumber"] else None

    @property
    def info(self) -> dict[str, Any] | None:
        return {item["displayName"]: item["value"] for item in self["extraMetadata"]} if self["extraMetadata"] else None
