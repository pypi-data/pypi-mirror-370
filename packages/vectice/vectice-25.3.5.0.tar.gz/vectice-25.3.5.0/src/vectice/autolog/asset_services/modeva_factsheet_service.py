from __future__ import annotations

from typing import Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.property_service import PropertyService
from vectice.autolog.asset_services.service_types.modeva_types import ModevaType
from vectice.autolog.asset_services.technique_service import TechniqueService


class ModevaFactSheetService(PropertyService, MetricService, TechniqueService):
    def __init__(self, key: str, asset: Any, data: dict):
        self._asset = asset
        self._key = key

        super().__init__(cell_data=data)

    def _get_model_info(self, model: Any):
        # estimator e.g sklearn / xgboost etc
        library = model.name.replace("'>", "")
        # Modeva wrapper
        technique = str(model.__class__).split(".")[-1].replace("'>", "")
        _, params = self._get_sklearn_or_xgboost_or_lgbm_info(model)
        return {
            "variable": self._key,
            "model": model,
            "library": library,
            "technique": technique,
            # "metrics": self._get_model_metrics(self._cell_data),
            "properties": params,
        }

    def get_asset(self):
        try:
            assets = {
                "variable": self._key,
                "dataset": None,
                "models": None,
                "validation_results": None,
                "asset_type": ModevaType.FACTSHEET,
            }
            # returns dataset / ds.data -> pd.DF
            dataset = self._asset.get_dataset().data
            assets["dataset"] = dataset

            # return estimator
            model = self._asset._LocalFactSheet__model
            if hasattr(self._asset, "_validation_test_results"):
                assets["validation_results"] = self._asset._validation_test_results
            if model:
                model_asset = self._get_model_info(model)
                assets["models"] = [model_asset]  # pyright: ignore[reportArgumentType]
                return assets
            if model is None:
                models = self._asset._LocalFactSheet__models
                model_assets = [self._get_model_info(model) for model in models]
                assets["models"] = model_assets  # pyright: ignore[reportArgumentType]
                return assets
        except Exception:
            pass
