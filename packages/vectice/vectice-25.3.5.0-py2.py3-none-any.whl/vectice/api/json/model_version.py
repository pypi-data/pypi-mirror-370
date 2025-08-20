from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from vectice.api._utils import read_nodejs_date
from vectice.api.json.artifact_version import ArtifactVersion
from vectice.api.json.json_type import TJSON
from vectice.api.json.model import ModelOutput

if TYPE_CHECKING:
    from datetime import datetime


class ModelVersionStatus(Enum):
    """Enumeration of the different model statuses."""

    EXPERIMENTATION = "EXPERIMENTATION"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"
    DISCARDED = "DISCARDED"


class ModelVersionInput(TJSON):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str:
        return str(self["description"])

    @property
    def repository(self) -> str:
        return str(self["repository"])

    @property
    def algorithm_name(self) -> str:
        return str(self["algorithmName"])

    @property
    def status(self) -> ModelVersionStatus:
        return ModelVersionStatus[str(self["status"])]

    @property
    def framework(self) -> str:
        return str(self["framework"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def is_starred(self) -> str:
        return str(self["isStarred"])

    @property
    def version(self) -> int:
        return int(self["version"])


class ModelVersionOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if "model" in self:
            self._model: ModelOutput = ModelOutput(**self["model"])
        else:
            self._model = None  # type: ignore

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str | None:
        if self.get("description", None):
            return str(self["description"])
        else:
            return None

    @property
    def created_date(self) -> datetime | None:
        return read_nodejs_date(self["createdDate"])

    @property
    def updated_date(self) -> datetime | None:
        if "updatedDate" in self:
            return read_nodejs_date(self["updatedDate"])
        else:
            return None

    @property
    def version(self) -> ArtifactVersion:
        return ArtifactVersion(version_number=self.version_number, version_name=self.name, version_id=self.id)

    @property
    def version_number(self) -> int:
        return int(self["versionNumber"])

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def author_id(self) -> int:
        return int(self["authorId"])

    @property
    def deleted_date(self) -> datetime | None:
        if "deletedDate" in self:
            return read_nodejs_date(self["deletedDate"])
        else:
            return None

    @property
    def project(self) -> str:
        return str(self["project"])

    @property
    def algorithm_name(self) -> str:
        return str(self["algorithmName"])

    @property
    def status(self) -> ModelVersionStatus:
        return ModelVersionStatus[str(self["status"])]

    @property
    def resources(self):
        return self.get("resources", None)

    @property
    def framework(self) -> str:
        return str(self["framework"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def is_starred(self) -> bool:
        return bool(self["isStarred"])

    @property
    def model_id(self) -> int:
        return int(self["modelId"])

    @property
    def model(self) -> ModelOutput:
        return self._model

    @property
    def metrics(self) -> dict[str, Any]:
        if "metrics" in self and self["metrics"] is not None:
            return cast(dict, self["metrics"])
        else:
            return {}

    @property
    def lineage(self) -> dict:
        return self["origin"]

    @property
    def origin_id(self) -> int:
        return int(self["origin"]["id"])
