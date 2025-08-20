from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectice.api._utils import read_nodejs_date
from vectice.api.json.json_type import TJSON
from vectice.api.json.project import ProjectOutput

if TYPE_CHECKING:
    from datetime import datetime


class CodeInput(TJSON):
    @property
    def code_id(self) -> int:
        return int(self["codeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str:
        return str(self["description"])

    @property
    def uri(self) -> str:
        return str(self["uri"])


class CodeOutput(TJSON):
    _project: ProjectOutput

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if "project" in self:
            self._project = ProjectOutput(**self["project"])
        else:
            self._project = None  # type: ignore

    @property
    def created_date(self) -> datetime | None:
        return read_nodejs_date(str(self["createdDate"]))

    @property
    def updated_date(self) -> datetime | None:
        return read_nodejs_date(str(self["updatedDate"]))

    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str | None:
        if "description" in self and self["description"] is not None:
            return str(self["description"])
        else:
            return None

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def author_id(self) -> int:
        return int(self["authorId"])

    @property
    def deleted_date(self) -> datetime | None:
        return read_nodejs_date(str(self["deletedDate"]))

    @property
    def version_number(self) -> int:
        return int(self["versionNumber"])

    @property
    def project(self) -> ProjectOutput:
        return self._project

    @project.setter
    def project(self, project: ProjectOutput):
        self._project = project

    @property
    def project_id(self) -> int | None:
        return int(self["projectId"])
