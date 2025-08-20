from __future__ import annotations

from datetime import datetime
from typing import Any

from vectice.api._utils import read_nodejs_date
from vectice.api.json.json_type import TJSON
from vectice.utils.logging_utils import get_review_status


class ReviewOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def message(self) -> str | None:
        value = self["message"]
        return str(value) if value else None

    @property
    def feedback(self) -> str | None:
        value = self["feedback"]
        return str(value) if value else None

    @property
    def created_date(self) -> datetime | None:
        if self["createdDate"] is not None:
            return read_nodejs_date(str(self["createdDate"]))
        return None

    @property
    def status(self) -> str:
        return get_review_status(self["status"])

    @property
    def creator(self) -> dict[str, str]:
        return {"name": self["createdBy"]["name"], "email": self["createdBy"]["email"]}

    @property
    def assignee(self) -> dict[str, str]:
        return {"name": self["reviewer"]["name"], "email": self["reviewer"]["email"]}
