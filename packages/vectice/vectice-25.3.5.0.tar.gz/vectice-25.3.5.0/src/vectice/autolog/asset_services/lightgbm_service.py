from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.property_service import PropertyService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.utils.common_utils import get_asset_name

if TYPE_CHECKING:
    from lightgbm.basic import Booster


class AutologLightgbmService(MetricService, PropertyService, TechniqueService):
    def __init__(
        self,
        key: str,
        asset: Booster,
        data: dict,
        custom_metrics_data: set[str | None],
        phase_name: str,
        prefix: str | None = None,
    ):
        self._asset = asset
        self._key = key
        self._model_name = get_asset_name(self._key, phase_name, prefix)

        super().__init__(cell_data=data, custom_metrics=custom_metrics_data)

    def get_asset(self):
        _, params = self._get_sklearn_or_xgboost_or_lgbm_info(self._asset)

        model = Model(
            library=ModelLibrary.LIGHTGBM.value,
            technique=self._get_model_technique(self._asset, ModelLibrary.LIGHTGBM),
            metrics=self._get_model_metrics(self._cell_data),
            properties=params,
            name=self._model_name,
            predictor=self._asset,
        )
        return {
            "variable": self._key,
            "model": model,
            "asset_type": VecticeType.MODEL,
        }
