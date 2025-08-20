from __future__ import annotations

from datetime import datetime
from typing import Any

from vectice.api._utils import read_nodejs_date
from vectice.api.json.json_type import TJSON
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput


class ReportOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int:
        return self["id"]

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def created_date(self) -> datetime | None:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> datetime | None:
        return read_nodejs_date(str(self["updatedDate"]))

    @property
    def model_version(self) -> ModelVersionRepresentationOutput | None:
        if self["modelVersion"] is not None:
            return ModelVersionRepresentationOutput(self["modelVersion"])

        return None

    @property
    def creator(self) -> dict[str, str]:
        return {"name": self["createdBy"]["name"], "email": self["createdBy"]["email"]}
