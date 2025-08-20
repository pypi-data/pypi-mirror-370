from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.autolog.asset_services.service_types.vectice_types import VecticeType

if TYPE_CHECKING:
    from ipywidgets import Output


class IpywidgetsOutputService:
    def __init__(
        self,
        key: str,
        asset: Output,
    ):
        self._asset = asset
        self._key = key

    def get_asset(self):
        return {
            "variable": self._key,
            "output": self._asset,
            "asset_type": VecticeType.IPYWIDGETS_OUTPUT,
        }
