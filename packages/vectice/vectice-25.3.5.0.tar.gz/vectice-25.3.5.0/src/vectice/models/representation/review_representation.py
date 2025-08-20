from __future__ import annotations

from typing import Any, Dict

from vectice.api.json.review import ReviewOutput
from vectice.utils.common_utils import (
    repr_class,
)


class ReviewRepresentation:
    """Represents the metadata of a Vectice review.

    A Review Representation shows information about a specific review from the Vectice app.
    It makes it easier to get and read this information through the API.

    Attributes:
        id (str): The unique identifier of the review.
        message (str | None): The message of the review.
        feedback (str | None): The feedback of the review.
        status (str): The status of the review (In Review, Approved, Rejected, or Cancelled).
        creator (Dict[str, str]): Creator of the review.
        assignee (Dict[str, str]): Assignee of the review.
    """

    def __init__(self, output: ReviewOutput):
        self.id = output.id
        self.message = output.message
        self.status = output.status
        self.feedback = output.feedback
        self.created_date = output.created_date
        self.creator = output.creator
        self.assignee = output.assignee

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the ReviewRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        return {
            "id": self.id,
            "message": self.message,
            "feedback": self.feedback,
            "status": self.status,
            "created_date": self.created_date,
            "creator": self.creator,
            "assignee": self.assignee,
        }
