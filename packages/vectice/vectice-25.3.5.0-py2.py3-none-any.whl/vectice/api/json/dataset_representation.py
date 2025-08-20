from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.api._utils import read_nodejs_date
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.json_type import TJSON

if TYPE_CHECKING:
    from datetime import datetime


class DatasetRepresentationOutput(TJSON):
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
        return self["type"]

    @property
    def origin(self) -> str:
        return self["sourceOrigin"]

    @property
    def description(self) -> str | None:
        return str(self["description"]) if self["description"] else None

    @property
    def version(self) -> DatasetVersionRepresentationOutput | None:
        if self["lastVersion"] is not None:
            return DatasetVersionRepresentationOutput(**self["lastVersion"])
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
