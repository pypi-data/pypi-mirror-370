from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.utils.common_utils import get_asset_name

if TYPE_CHECKING:
    from statsmodels.base.wrapper import ResultsWrapper


class AutologStatsModelWrapperService(MetricService, TechniqueService):
    def __init__(
        self,
        key: str,
        asset: ResultsWrapper,
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
        _, params = self._get_statsmodel_info(self._asset)
        model_summary = self._asset.summary().as_text()
        model = Model(
            library=ModelLibrary.STATSMODEL.value,
            technique=self._get_model_technique(self._asset, ModelLibrary.STATSMODEL),
            metrics=self._get_statsmodels_metrics(self._asset),
            properties=params,
            name=self._model_name,
            predictor=self._asset,
        )
        return {
            "variable": self._key,
            "model": model,
            "summary": model_summary,
            "asset_type": VecticeType.MODEL,
        }

    def _get_statsmodel_info(self, model: ResultsWrapper) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            # model params
            model_params = {"model_type": model.model.__class__.__name__, "formula": model.model.formula}
            # statsmodels fitted/Resultswrapper
            params = {str(key): value for key, value in model.params.items() if value is not None}
            model_params.update(params)
            return "statsmodel", model_params
        except AttributeError:
            return None, None
