from __future__ import annotations

from typing import Any

from vectice.api.json.json_type import TJSON
from vectice.api.json.phase import PhaseOutput


class RequirementOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if "phase" in self:
            self._phase: PhaseOutput = PhaseOutput(**self["phase"])
        else:
            self._phase = None  # type: ignore

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str | None:
        return str(self["description"])
