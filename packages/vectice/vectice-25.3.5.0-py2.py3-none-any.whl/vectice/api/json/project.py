from __future__ import annotations

from typing import Any

from vectice.api.json.json_type import TJSON
from vectice.api.json.workspace import WorkspaceOutput
from vectice.types.project import ProjectInput


class ProjectCreateInput(TJSON):
    def __init__(self, project: ProjectInput):
        self["name"] = project["name"]
        if "template" in project:
            self["templateName"] = project["template"]
        if "copy_project_id" in project:
            self["copyProjectId"] = project["copy_project_id"]
        if "description" in project:
            self["description"] = project["description"]


class ProjectOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if "workspace" in self:
            self._workspace: WorkspaceOutput = WorkspaceOutput(**self["workspace"])

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

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
    def workspace(self) -> WorkspaceOutput:
        return self._workspace
