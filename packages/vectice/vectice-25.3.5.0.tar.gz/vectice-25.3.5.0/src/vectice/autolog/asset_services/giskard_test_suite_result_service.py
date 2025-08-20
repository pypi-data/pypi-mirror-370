from __future__ import annotations

from typing import Any

from vectice.autolog.asset_services.service_types.giskard_types import GiskardType
from vectice.utils.common_utils import temp_directory

GISKARD_TEMP_DIR = "giskard"


class GiskardTestSuiteResultService:
    def __init__(self, key: str, asset: Any):
        self._asset = asset
        self._key = key
        self._temp_dir = temp_directory(GISKARD_TEMP_DIR)

    def get_asset(self):
        asset = {
            "variable": self._key,
            "suite_name": self._asset.suite.name,
            "attachment": None,
            "asset_type": GiskardType.TEST_SUITE_RESULT,
        }
        html_content = self._asset._repr_html_()

        filename_path = self._temp_dir / f"{self._key}_test_suite.html"
        filename = filename_path.as_posix()

        with open(filename, "w") as file:
            file.write(html_content)

        asset["attachment"] = filename
        return asset
