from __future__ import annotations

from typing import Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.property_service import PropertyService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.utils.common_utils import get_asset_name


class AutologPysparkMLService(MetricService, PropertyService, TechniqueService):
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
        self._phase_name = phase_name
        self._model_name = get_asset_name(self._key, phase_name, prefix)
        self._library = ModelLibrary.PYSPARKML

        super().__init__(cell_data=data, custom_metrics=custom_metrics_data)

    def get_asset(self, asset: Any | None = None):
        # Pipeline isn't fitted and PipelineModel has a fit
        from pyspark.ml.pipeline import PipelineModel
        from pyspark.ml.tuning import CrossValidatorModel

        original_asset = self._asset
        if asset is not None:
            self._asset = asset

        if isinstance(self._asset, PipelineModel):
            return self.get_pipeline()
        if isinstance(self._asset, CrossValidatorModel):
            return self.get_validator()

        # .extractParamMap() as hash / params as list
        parameters = self._get_pyspark_parameters(self._asset)
        metrics = self._get_model_metrics(self._cell_data)

        # only estimators will have a summary
        if hasattr(self._asset, "hasSummary") and self._asset.hasSummary:
            summary_metrics = self._get_pyspark_ml_summary_metrics(self._asset.summary)
            metrics.update({key: value for key, value in summary_metrics.items() if key not in metrics})

        asset = self._get_pyspark_asset(metrics, parameters)
        if asset:
            self._asset = original_asset
        return asset

    def get_validator(self):
        # just get the tuning parameters
        validator_prefix = self._asset.uid.split("_")[0]

        parameters = self._get_pyspark_parameters(self._asset, validator_prefix)
        metrics = self._get_model_metrics(self._cell_data)

        best_model = self._asset.bestModel
        best_model_prefix = best_model.uid.split("_")[0]
        best_model_params = self._get_pyspark_parameters(self._asset, best_model_prefix)
        parameters.update(best_model_params)

        # only estimators will have a summary
        if hasattr(best_model, "hasSummary") and best_model.hasSummary:
            best_model_metrics = self._get_pyspark_ml_summary_metrics(best_model.summary, best_model_prefix)
            metrics.update(best_model_metrics)

        asset = self._get_pyspark_asset(metrics, parameters)
        return asset

    def get_pipeline(self):
        # Pipeline has getStages & PipelineModel has stages
        stages = self._asset.stages

        parameters = self._get_pyspark_parameters(self._asset)

        metrics = self._get_model_metrics(self._cell_data)
        # only estimators will have a summary
        if hasattr(self._asset, "hasSummary") and self._asset.hasSummary:
            summary_metrics = self._get_pyspark_ml_summary_metrics(self._asset.summary)
            metrics.update(summary_metrics)

        for stage in stages:
            parsed_asset = self.get_asset(stage)
            model = parsed_asset["model"]
            prefix = model.technique
            if model.metrics:
                parsed_asset_metrics = {f"{prefix}_{metric.value}": metric.value for metric in parsed_asset["model"].metrics}  # type: ignore[reportAttributeAccessIssue]
                metrics.update(parsed_asset_metrics)
            if model.properties:
                parsed_asset_parameters = {f"{prefix}_{property.key}": property.value for property in parsed_asset["model"].properties}  # type: ignore[reportAttributeAccessIssue]
                parameters.update(parsed_asset_parameters)

        asset = self._get_pyspark_asset(metrics, parameters)
        return asset

    def _get_pyspark_asset(self, metrics: dict, parameters: dict) -> dict[str, Any]:
        model = Model(
            library=self._library.value,
            technique=self._get_model_technique(self._asset, self._library),
            metrics=metrics,
            properties=parameters,
            name=self._model_name,
            predictor=self._asset,
        )
        return {
            "variable": self._key,
            "model": model,
            "asset_type": VecticeType.MODEL,
        }
