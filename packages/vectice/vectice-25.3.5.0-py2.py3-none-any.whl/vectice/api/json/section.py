from __future__ import annotations

from vectice.api.json.requirement import RequirementOutput


class SectionOutput(RequirementOutput):
    @property
    def artifacts_count(self) -> int:
        return int(self["paginatedArtifacts"]["total"])
