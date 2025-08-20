from __future__ import annotations

import logging
from typing import Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.property_service import PropertyService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.utils.common_utils import flatten_dict, get_asset_name, temp_directory

_logger = logging.getLogger(__name__)

H2O_TEMP_DIR = "h2o"


class AutologH2oEstimatorService(MetricService, PropertyService, TechniqueService):
    def __init__(
        self,
        key: str,
        asset: Any,
        data: dict,
        custom_metrics_data: set[str | None],
        phase_name: str,
        prefix: str | None = None,
    ):
        self._asset = asset
        self._key = key
        self._temp_dir = temp_directory(H2O_TEMP_DIR)
        self._model_name = get_asset_name(self._key, phase_name, prefix)

        super().__init__(cell_data=data, custom_metrics=custom_metrics_data)

    def get_asset(self):
        temp_files = []
        library = ModelLibrary.H2O

        try:
            params = flatten_dict(
                {
                    str(key): value
                    for key, value in self._asset.get_params().items()  # pyright: ignore[reportAttributeAccessIssue]
                    if value is not None and bool(str(value))
                }
            )
            model = Model(
                library=library.value,
                technique=self._get_model_technique(self._asset, ModelLibrary.H2O),
                metrics=self._get_model_metrics(self._cell_data),
                properties=params,
                name=self._model_name,
                predictor=self._asset,
                attachments=temp_files,
            )
            return {
                "variable": self._key,
                "model": model,
                "asset_type": VecticeType.MODEL,
            }
        except Exception as e:
            _logger.debug(f"Failed to get asset from {self._asset.__class__.__name__}: {e!s}.")
