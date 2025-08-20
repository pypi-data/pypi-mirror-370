from __future__ import annotations

from vectice.api.json.compatibility import CompatibilityOutput
from vectice.api.rest_api import RestApi


class CompatibilityApi(RestApi):
    def check_version(self) -> CompatibilityOutput:
        response = self.get("/metadata/compatibility")
        if "message" not in response.keys():
            return CompatibilityOutput(message="", status="OK")
        else:
            return CompatibilityOutput(**response)
