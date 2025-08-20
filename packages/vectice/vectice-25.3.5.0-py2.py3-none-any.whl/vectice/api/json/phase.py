from __future__ import annotations

from enum import Enum
from typing import Any

from vectice.api.json.json_type import TJSON
from vectice.api.json.project import ProjectOutput


class PhaseStatus(Enum):
    """Enumeration of the different phase statuses."""

    NotStarted = "NotStarted"
    InProgress = "Draft"
    Completed = "Completed"
    InReview = "InReview"


class PhaseOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project: ProjectOutput | None = None
        if "parent" in self:
            self._project = ProjectOutput(**self["parent"])

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def index(self) -> int:
        return int(self["index"])

    @property
    def status(self) -> PhaseStatus:
        return PhaseStatus(self["status"])

    @property
    def project(self) -> ProjectOutput | None:
        return self._project

    @property
    def steps_count(self) -> int | None:
        return int(self["stepsCount"]) if "stepsCount" in self else None

    @property
    def iterations_count(self) -> int | None:
        return (
            int(self["iterationsCount"]["total"])
            if "iterationsCount" in self and "total" in self["iterationsCount"]
            else None
        )

    @property
    def active_iterations_count(self) -> int | None:
        if "iterationsCount" in self:
            iter_count = self["iterationsCount"]
            not_started = int(iter_count["notStarted"])
            in_progress = int(iter_count["inProgress"])
            in_review = int(iter_count["inReview"])
            return not_started + in_progress + in_review

        return None
