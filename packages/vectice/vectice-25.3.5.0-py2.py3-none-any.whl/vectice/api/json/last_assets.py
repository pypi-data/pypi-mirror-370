from __future__ import annotations

from enum import Enum
from typing import Any

from vectice.api.json.json_type import TJSON


class ActivityTargetType(Enum):
    Code = "Code"
    CodeVersion = "CodeVersion"
    DataResource = "DataResource"
    DataSet = "DataSet"
    DataSetVersion = "DataSetVersion"
    Datasheet = "Datasheet"
    Iteration = "Iteration"
    Review = "Review"
    ReviewComment = "ReviewComment"
    IterationStep = "IterationStep"
    Model = "Model"
    ModelCard = "ModelCard"
    ModelVersion = "ModelVersion"
    Phase = "Phase"
    Project = "Project"
    StepDefinition = "StepDefinition"
    Workspace = "Workspace"
    WorkspaceUser = "WorkspaceUser"


class UserActivity(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int:
        return int(self["targetId"])

    @property
    def name(self) -> str:
        return str(self["targetName"])

    @property
    def target_type(self) -> ActivityTargetType:
        return ActivityTargetType(self["targetType"])
