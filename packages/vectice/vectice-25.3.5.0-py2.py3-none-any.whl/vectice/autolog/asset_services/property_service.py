from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lightgbm.basic import Booster
    from pyspark.ml.base import Model
    from sklearn.base import BaseEstimator

    from vectice.autolog.model_types import ModelTypes


####### PropertyService for sklearn, xgboost & lightgbm
class PropertyService:

    def _get_model_library(self, model: ModelTypes):
        if "xgboost" in str(model.__class__):
            return "xgboost"
        if "lightgbm" in str(model.__class__):
            return "lightgbm"
        if str(model.__class__.__module__) == "sklearn.model_selection._search":
            return "sklearn-searchcv"
        return "sklearn"

    def _get_lightgbm_info(self, model: Booster) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            params = {
                key: value
                for key, value in model._get_loaded_param().items()  # pyright: ignore[reportPrivateUsage]
                if value is not None
            }
            return "lightgbm", params
        except AttributeError:
            return None, None

    def _get_sklearn_or_xgboost_or_lgbm_info(
        self, model: BaseEstimator | Booster
    ) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        def _flatten_dict(params: dict, parent_key: str = "") -> dict:
            def _reduce_items(acc: list, item: tuple) -> list:
                key, value = item
                new_key = f"{parent_key}_{key}" if parent_key else key
                return (
                    [*acc, *_flatten_dict(value, new_key).items()]
                    if isinstance(value, dict)
                    else [*acc, (new_key, value)]
                )

            return dict(reduce(_reduce_items, params.items(), []))

        try:
            library = self._get_model_library(model)  # pyright: ignore[reportArgumentType]
            base_parameters = (
                model.best_estimator_  # pyright: ignore[reportAttributeAccessIssue]
                if library == "sklearn-searchcv"
                else model
            )
            params = _flatten_dict(
                {
                    str(key): value
                    for key, value in base_parameters.get_params().items()  # pyright: ignore[reportAttributeAccessIssue]
                    if value is not None and bool(str(value))
                }
            )
            return library, params
        except AttributeError:
            return None, None

    def _get_pyspark_parameters(self, model: Model, prefix: str | None = None) -> dict[str, Any]:
        parameters = {}
        for param, value in model.extractParamMap().items():
            if value and isinstance(value, (str, int)) and not isinstance(param, (dict, set)):
                if prefix is not None:
                    parameters[f"{prefix}_{param.name}"] = value
                else:
                    parameters[param.name] = value
        return parameters
