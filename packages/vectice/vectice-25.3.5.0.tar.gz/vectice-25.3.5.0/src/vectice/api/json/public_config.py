from __future__ import annotations

from enum import Enum
from typing import Any

from vectice.api.json.json_type import TJSON


class PublicConfigOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def versions(self) -> list["VersionOutput"]:
        return [VersionOutput(**version) for version in self["versions"]]


class VersionOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def version(self) -> str:
        return str(self["version"])

    @property
    def artifact_name(self) -> "ArtifactName":
        return ArtifactName(self["artifactName"])


class ArtifactName(Enum):
    GLOBAL = "GLOBAL"
    BACKEND = "BACKEND"
