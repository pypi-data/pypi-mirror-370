from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from vectice.api.json.report import ReportOutput
from vectice.utils.common_utils import (
    repr_class,
)

if TYPE_CHECKING:
    from vectice.api.client import Client


class ReportRepresentation:
    """Represents the metadata of a Vectice report.
    A Report Representation shows information about a specific issue from the Vectice app.
    It makes it easier to get and read this information through the API.

    Attributes:
        id (int): The unique identifier of the issue.
        name (str): The name of the issue.
        creator (Dict[str, str]): Creator of the issue.
        created_date (datetime): The created date of the report.
        updated_date (datetime): The last updated date of the report.
        model_version (ModelVersionRepresentation | None): The model version of the report.
    """

    def __init__(self, output: ReportOutput, client: Client):
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        self.id = output.id
        self.name = output.name
        self.creator = output.creator
        self.created_date = output.created_date
        self.updated_date = output.updated_date
        self.model_version = ModelVersionRepresentation(output.model_version, client) if output.model_version else None

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the ReportRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "creator": self.creator,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "model_version": self.model_version.asdict() if self.model_version else None,
        }
