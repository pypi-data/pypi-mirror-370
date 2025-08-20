from __future__ import annotations

from abc import abstractmethod
from importlib.util import find_spec
from typing import Any, Protocol

from vectice.api.http_error_handlers import VecticeException
from vectice.autolog.asset_services import (
    AutologCatboostService,
    AutologH2oDisplayService,
    AutologH2oEstimatorService,
    AutologH2OFrameService,
    AutologKerasService,
    AutologLightgbmService,
    AutologPandasService,
    AutologPysparkMLService,
    AutologPysparkService,
    AutologPytorchService,
    AutologSklearnService,
    AutologStatsModelWrapperService,
    AutologVecticeAssetService,
    GiskardQATestSetService,
    GiskardRAGReportService,
    GiskardScanReportService,
    GiskardTestSuiteResultService,
    IpywidgetsOutputService,
    ModevaFactSheetService,
    ModevaValidationResult,
    VecticeObjectClasses,
)


class IAutologService(Protocol):
    @abstractmethod
    def get_asset(self) -> dict[str, Any] | None: ...


class AssetFactory:
    @staticmethod
    def get_asset_service(
        key: str,
        asset: Any,
        data: dict,
        phase_name: str,
        custom_metrics: set[str | None] = set(),
        raw_cells_data: list = [],
        capture_schema_only: bool = False,
        prefix: str | None = None,
    ) -> IAutologService:
        is_pandas = find_spec("pandas") is not None
        is_pyspark = find_spec("pyspark") is not None
        is_lgbm = find_spec("lightgbm") is not None
        is_sklearn = find_spec("sklearn") is not None
        is_catboost = find_spec("catboost") is not None
        is_keras = find_spec("keras") is not None
        is_statsmodels = find_spec("statsmodels") is not None
        is_pytorch = find_spec("torch") is not None
        is_modeva = find_spec("modeva") is not None
        is_giskard = find_spec("giskard") is not None
        is_ipywidgets = find_spec("ipywidgets") is not None
        is_h2o = find_spec("h2o") is not None

        if is_giskard:
            from giskard.core.suite import TestSuiteResult  # type: ignore[reportMissingImports]
            from giskard.rag import QATestset  # type: ignore[reportMissingImports]
            from giskard.rag.report import RAGReport  # type: ignore[reportMissingImports]
            from giskard.scanner.report import ScanReport  # type: ignore[reportMissingImports]

            if isinstance(asset, ScanReport):
                return GiskardScanReportService(key, asset, data)
            if isinstance(asset, RAGReport):
                return GiskardRAGReportService(key, asset)
            if isinstance(asset, QATestset):
                return GiskardQATestSetService(key, asset)
            if isinstance(asset, TestSuiteResult):
                return GiskardTestSuiteResultService(key, asset)

        if is_modeva:
            from modeva import FactSheet  # type: ignore[reportMissingImports]
            from modeva.utils.results import ValidationResult  # type: ignore[reportMissingImports]

            if isinstance(asset, FactSheet):
                return ModevaFactSheetService(key, asset, {})
            if isinstance(asset, ValidationResult):
                return ModevaValidationResult(key, asset, {})

        if is_pandas:
            from pandas import DataFrame

            if isinstance(asset, DataFrame):
                return AutologPandasService(key, asset, phase_name, raw_cells_data, capture_schema_only, prefix)

        if is_pyspark:
            # base estimator class, Predictor is for a model with no fit
            from pyspark.ml.base import Model, PredictionModel
            from pyspark.ml.pipeline import PipelineModel
            from pyspark.ml.tuning import CrossValidatorModel

            # pyspark evaluators
            # Pipeline isn't fitted and PipelineModel has a fit
            # clustering models e.g kmeans
            # JavaParams is for pipeline components (might remove/move logic due to overlaps)
            from pyspark.ml.wrapper import JavaModel

            # , Evaluator, JavaParams, Pipeline
            pyspark_service_types = (CrossValidatorModel, PredictionModel, JavaModel, Model, PipelineModel)

            from pyspark.sql import DataFrame as SparkDF
            from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDF

            if isinstance(asset, (SparkDF, SparkConnectDF)):
                return AutologPysparkService(key, asset, phase_name, raw_cells_data, capture_schema_only, prefix)

            if isinstance(asset, pyspark_service_types):
                return AutologPysparkMLService(key, asset, data, custom_metrics, phase_name, prefix)

        if is_lgbm:
            from lightgbm.basic import Booster

            if isinstance(asset, Booster):
                return AutologLightgbmService(key, asset, data, custom_metrics, phase_name, prefix)

        if is_catboost:
            from catboost.core import CatBoost

            if isinstance(asset, CatBoost):
                return AutologCatboostService(key, asset, data, custom_metrics, phase_name, prefix)
        if is_h2o:
            from h2o.display import H2ODisplay  # type: ignore[reportMissingImports]
            from h2o.estimators import H2OEstimator  # type: ignore[reportMissingImports]
            from h2o.frame import H2OFrame  # type: ignore[reportMissingImports]

            # We do not want to accidentally log models or frames as H2ODisplay objects.
            if isinstance(asset, H2ODisplay) and not isinstance(asset, (H2OEstimator, H2OFrame)):
                return AutologH2oDisplayService(key, asset, phase_name, prefix)

            if isinstance(asset, H2OEstimator):
                return AutologH2oEstimatorService(key, asset, data, custom_metrics, phase_name, prefix)

            if isinstance(asset, H2OFrame):
                return AutologH2OFrameService(key, asset, phase_name, raw_cells_data, capture_schema_only, prefix)

        if is_keras:
            from keras.models import Model as KerasModel  # type: ignore[reportMissingImports]

            if isinstance(asset, KerasModel):
                return AutologKerasService(key, asset, data, custom_metrics, phase_name, prefix)

        if is_pytorch:
            from torch.nn import Module

            if isinstance(asset, Module):
                return AutologPytorchService(key, asset, data, custom_metrics, phase_name, prefix)

        if isinstance(asset, VecticeObjectClasses):
            return AutologVecticeAssetService(key, asset)  # type: ignore[reportArgumentType]

        if is_statsmodels:
            from statsmodels.base.wrapper import ResultsWrapper

            if isinstance(asset, ResultsWrapper):
                return AutologStatsModelWrapperService(key, asset, data, custom_metrics, phase_name, prefix)

        if is_ipywidgets:
            from ipywidgets import Output

            if isinstance(asset, Output):
                return IpywidgetsOutputService(key, asset)

        if is_sklearn:
            return AutologSklearnService(key, asset, data, custom_metrics, phase_name, prefix)

        raise VecticeException(f"Asset {asset} of type ({type(asset)!r}) not handled")
