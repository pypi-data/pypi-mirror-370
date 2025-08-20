from __future__ import annotations

from typing import Any

from vectice.autolog.asset_services.service_types.giskard_types import GiskardType


class GiskardQATestSetService:
    def __init__(self, key: str, asset: Any):
        self._asset = asset
        self._key = key

    def get_asset(self):
        from vectice import Table

        assets = {
            "variable": self._key,
            "table": None,
            "dataframe": None,
            "csv": None,
            "asset_type": GiskardType.QATESTSET,
        }
        try:
            testset_df = self._asset.to_pandas()
            assets["table"] = Table(testset_df, "QATestset")  # type: ignore[reportArgumentType]
            assets["dataframe"] = testset_df
            filename = "qatestset.csv"
            testset_df.to_csv(filename)
            assets["csv"] = filename
            return assets
        except Exception:
            pass
