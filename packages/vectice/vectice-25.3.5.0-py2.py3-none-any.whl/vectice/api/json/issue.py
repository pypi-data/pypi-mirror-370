from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from vectice.api._utils import read_nodejs_date
from vectice.api.json.json_type import TJSON
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput
from vectice.api.json.report import ReportOutput


class IssueStatus(Enum):
    Cancelled = "Cancelled"
    Completed = "Completed"
    InProgress = "InProgress"
    NotStarted = "NotStarted"
    RemediationPending = "RemediationPending"


class IssueSeverity(Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Undefined = "Undefined"


class IssueOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int:
        return self["id"]

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def severity(self) -> IssueSeverity | None:
        return IssueSeverity(self["severity"]) if self["severity"] else None

    @property
    def status(self) -> IssueStatus:
        return IssueStatus(self["status"])

    @property
    def model_version(self) -> ModelVersionRepresentationOutput | None:
        if "modelVersion" in self and self["modelVersion"] is not None:
            return ModelVersionRepresentationOutput(self["modelVersion"])
        return None

    @property
    def report(self) -> ReportOutput | None:
        if self["report"] is not None:
            return ReportOutput(self["report"])
        return None

    @property
    def due_date(self) -> datetime | None:
        if self["dueDate"] is not None:
            return read_nodejs_date(str(self["dueDate"]))
        return None

    @property
    def created_date(self) -> datetime | None:
        if self["createdDate"] is not None:
            return read_nodejs_date(str(self["createdDate"]))
        return None

    @property
    def owner(self) -> dict[str, str]:
        return {"name": self["owner"]["name"], "email": self["owner"]["email"]}

    @property
    def assignee(self) -> dict[str, str] | None:
        return {"name": self["reviewer"]["name"], "email": self["reviewer"]["email"]} if self["reviewer"] else None
