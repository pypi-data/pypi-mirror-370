from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from vectice.api.json.issue import IssueOutput
from vectice.models.representation.report_representation import ReportRepresentation
from vectice.utils.common_utils import (
    repr_class,
)

if TYPE_CHECKING:
    from vectice.api.client import Client


class IssueRepresentation:
    """Represents the metadata of a Vectice issue.

    An Issue Representation shows information about a specific issue from the Vectice app.
    It makes it easier to get and read this information through the API.

    Attributes:
        id (int): The unique identifier of the issue.
        name (str): The name of the issue.
        status (str): The status of the issue (Cancelled, Completed, InProgress, NotStarted, or RemediationPending).
        severity (str | None): The severity of the issue (Low, Medium, or High).
        due_date (datetime | None): The due date of the issue.
        model_version (ModelVersionRepresentation | None): The model version related to this finding.
        created_date (datetime | None): The date when the issue was created.
        report (ReportRepresentation | None): The report related to this finding.
        owner (Dict[str, str]): Owner of the issue.
        assignee (Dict[str, str]): Assignee of the issue.
    """

    def __init__(self, output: IssueOutput, client: Client):
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        self.id = output.id
        self.name = output.name
        self.status = output.status
        self.severity = output.severity
        self.due_date = output.due_date
        self.model_version = (
            ModelVersionRepresentation(output.model_version, client) if output.model_version is not None else None
        )
        self.created_date = output.created_date
        self.report = ReportRepresentation(output.report, client) if output.report is not None else None
        self.owner = output.owner
        self.assignee = output.assignee

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the IssueRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "severity": self.severity,
            "due_date": self.due_date,
            "model_version": (self.model_version.asdict() if self.model_version else None),
            "created_date": self.created_date,
            "report": (self.report.asdict() if self.report else None),
            "owner": self.owner,
            "assignee": self.assignee,
        }
