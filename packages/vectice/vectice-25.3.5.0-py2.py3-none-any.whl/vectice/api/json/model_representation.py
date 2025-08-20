from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.api._utils import read_nodejs_date
from vectice.api.json.json_type import TJSON
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput

if TYPE_CHECKING:
    from datetime import datetime


class ModelRepresentationOutput(TJSON):
    @property
    def created_date(self) -> datetime | None:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> datetime | None:
        return read_nodejs_date(str(self["updatedDate"]))

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def description(self) -> str | None:
        return str(self["description"]) if self["description"] else None

    @property
    def version(self) -> ModelVersionRepresentationOutput | None:
        if self["lastVersion"] is not None:
            return ModelVersionRepresentationOutput(**self["lastVersion"])
        else:
            return None

    @property
    def project_id(self) -> str | None:
        if "project" in self:
            return str(self["project"]["vecticeId"])
        return None

    @property
    def total_number_of_versions(self) -> int:
        return int(self["versionCount"])

    @property
    def version_stats(self) -> dict[str, int] | None:
        if "versionStats" in self:
            return self["versionStats"]
        return self["versionStats"]
