from typing import Any

from vectice.api.json.json_type import TJSON
from vectice.api.json.workspace import WorkspaceOutput


class UserOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class UserAndDefaultWorkspaceOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def default_workspace(self) -> WorkspaceOutput:
        return WorkspaceOutput(**self["defaultWorkspace:"])

    @property
    def user(self) -> UserOutput:
        return UserOutput(**self["user"])
