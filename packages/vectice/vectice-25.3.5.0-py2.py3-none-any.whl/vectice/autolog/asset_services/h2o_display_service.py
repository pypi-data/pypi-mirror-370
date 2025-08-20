from __future__ import annotations

import logging
from typing import Any

from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.models.table import Table
from vectice.utils.common_utils import get_asset_name

_logger = logging.getLogger(__name__)


class AutologH2oDisplayService:
    def __init__(
        self,
        key: str,
        asset: Any,
        phase_name: str,
        prefix: str | None = None,
    ):
        self._asset = asset
        self._key = key
        self._display_name = get_asset_name(self._key, phase_name, prefix)

    def get_asset(self):
        try:
            dataframe = self._asset.as_data_frame()
            table = Table(dataframe=dataframe, name=self._display_name)

            return {"variable": self._key, "vectice_object": table, "asset_type": VecticeType.VECTICE_OBJECT}
        except Exception as e:
            _logger.debug(f"Failed to get asset from {self._asset.__class__.__name__}: {e!s}.")
