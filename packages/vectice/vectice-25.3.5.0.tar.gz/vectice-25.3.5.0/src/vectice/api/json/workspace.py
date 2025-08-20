from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from vectice.api.json.json_type import TJSON

if TYPE_CHECKING:
    pass


@dataclass
class WorkspaceInput:
    name: str | None
    description: str | None


class WorkspaceOutput(TJSON):
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
