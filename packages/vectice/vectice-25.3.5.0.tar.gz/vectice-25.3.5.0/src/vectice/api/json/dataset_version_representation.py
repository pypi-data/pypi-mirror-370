from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from vectice.api._utils import read_nodejs_date
from vectice.api.json.json_type import TJSON

if TYPE_CHECKING:
    from datetime import datetime

    from vectice.api.json.dataset_representation import DatasetRepresentationOutput


class DatasetVersionRepresentationOutput(TJSON):
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
    def dataset_id(self) -> str | None:
        if "dataSet" in self:
            return str(self["dataset"]["vecticeId"])
        return None

    @property
    def phase_origin(self) -> str | None:
        origins = self.get("origins", {})
        phase = origins.get("phase")
        if phase and "vecticeId" in phase:
            return str(phase["vecticeId"])
        return None

    @property
    def iteration_origin(self) -> str | None:
        origins = self.get("origins", {})
        iteration = origins.get("iteration")
        if iteration and "vecticeId" in iteration:
            return str(iteration["vecticeId"])
        return None

    @property
    def creator(self) -> dict[str, str]:
        return {"name": self["createdBy"]["name"], "email": self["createdBy"]["email"]}

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def origin(self) -> str:
        return str(self["sourceOrigin"])

    @property
    def dataset_name(self) -> str | None:
        if "dataSet" in self:
            return str(self["dataSet"]["name"])
        return None

    @property
    def dataset(self) -> DatasetRepresentationOutput:
        from vectice.api.json.dataset_representation import DatasetRepresentationOutput

        return DatasetRepresentationOutput(**self["dataSet"])

    @property
    def description(self) -> str | None:
        return str(self["description"]) if self["description"] else None

    @property
    def project_id(self) -> str | None:
        if "dataSet" in self:
            return str(self["dataSet"]["project"]["vecticeId"])
        return None

    @property
    def properties(self) -> List[Dict[str, Any]]:
        return self["properties"]

    @property
    def resources(self) -> List[Dict[str, Any]]:
        for source in self["datasetSources"]:
            source["usage"] = "GENERIC" if source["usage"] is None else source["usage"]
            source["resource_type"] = source.pop("usage")
            source["number_of_items"] = source.pop("itemsCount")
            source["total_number_of_columns"] = source.pop("columnsCount")

        return self["datasetSources"]

    @property
    def is_starred(self) -> bool:
        return bool(self["isStarred"])
