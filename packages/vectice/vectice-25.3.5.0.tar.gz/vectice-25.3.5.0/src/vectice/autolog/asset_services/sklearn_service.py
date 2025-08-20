from __future__ import annotations

import logging
from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, Callable

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.property_service import PropertyService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.models.table import Table
from vectice.utils.common_utils import get_asset_name, temp_directory

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.autolog.model_types import ModelTypes
    from vectice.models.table import Table

_logger = logging.getLogger(__name__)

SKLEARN_TEMP_DIR = "sklearn"
IS_PANDAS = find_spec("pandas") is not None


def identify_estimator(asset: Any) -> bool:
    """Identify if the asset is a scikit-learn or xgboost estimator."""
    estimators = {"regressor", "classifier", "clusterer"}
    # prevent seeing is_classifier and is_regressor stdout for sklearn > 1.6.0
    try:
        # sklearn > 1.6.1, xgboost does not support this yet
        estimator_type = asset.__sklearn_tags__().estimator_type
        # It's possible to have a scenario where the tags are None but implemented in XGBoost, due to the sklearn changes
        if estimator_type:
            return estimator_type in estimators

    except Exception:
        pass

    try:
        # sklearn < 1.6.1, xgboost temp fallback. Current sklearn integration is behind
        return getattr(asset, "_estimator_type", None) in estimators

    except Exception:
        pass
    return False


class AutologSklearnService(MetricService, PropertyService, TechniqueService):
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
        self._temp_dir = temp_directory(SKLEARN_TEMP_DIR)
        self._model_name = get_asset_name(self._key, phase_name, prefix)

        super().__init__(cell_data=data, custom_metrics=custom_metrics_data)

    def get_asset(self):
        """This method processes scikit-learn estimators, pipelines, and model search objects to create a standardized Model asset.
        It identifies the type of sklearn object (estimator, pipeline, or search), extracts relevant information such as parameters and metrics,
        and generates appropriate attachments based on the model type. For search objects, it extracts search results and hyperparameter space tables.
        For pipelines, it generates HTML and JSON representations.
        For regular estimators, it extracts model parameters and metrics.

        Note:
        Get the model asset if it is a valid sklearn or xgboost model. xgboost relies on BaseEstimator.
        lightgbm has Booster and sklearn API which uses BaseEstimator.
        """
        from sklearn.pipeline import Pipeline

        temp_files = []
        is_estimator = identify_estimator(self._asset)
        is_pipeline = isinstance(self._asset, Pipeline)
        is_search = is_estimator and str(self._asset.__class__.__module__) == "sklearn.model_selection._search"

        if not (is_estimator or is_pipeline or is_search):
            return None

        if is_search:
            library = ModelLibrary.SKLEARN_SEARCH
            tables = self._get_sklearn_search_results_and_space_tables(self._asset, self._model_name)
            temp_files.extend(tables)

        elif is_pipeline:
            library = ModelLibrary.SKLEARN_PIPELINE
            html_and_json_paths = self._get_sklearn_pipeline_html_and_json(self._asset, self._model_name)
            temp_files.extend(html_and_json_paths)

        else:
            library = ModelLibrary.SKLEARN

        try:
            # TODO fix regex picking up classes
            # Ignore Initialized variables e.g LogisticRegression Class
            self._asset.get_params()  # pyright: ignore[reportGeneralTypeIssues]
            _, params = self._get_sklearn_or_xgboost_or_lgbm_info(self._asset)
            model = Model(
                library=library.value,
                technique=self._get_model_technique(self._asset, ModelLibrary.SKLEARN),
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

    def _get_sklearn_pipeline_html_and_json(self, pipeline: ModelTypes, model_name: str) -> list[str]:
        """Generate JSON and HTML representations of sklearn pipeline."""
        from sklearn.utils import estimator_html_repr

        from vectice.utils.sklearn_pipe_utils import pipeline_to_json

        file_generators = [("json", "json", pipeline_to_json), ("html", "utf-8", estimator_html_repr)]

        return [
            file_path
            for extension, encoding, generator in file_generators
            if (file_path := self._create_pipeline_file(pipeline, model_name, extension, encoding, generator))
        ]

    def _create_pipeline_file(
        self,
        pipeline: ModelTypes,
        model_name: str,
        extension: str,
        encoding: str,
        generator_func: Callable[[ModelTypes], str | None],
    ) -> str | None:
        """Create a pipeline representation file."""
        try:
            content = generator_func(pipeline)
            if not content:
                return None

            file_path = self._temp_dir / f"{model_name}_pipeline.{extension}"
            with open(file_path, "w", encoding=encoding) as file:
                file.write(content)

            return file_path.as_posix()

        except Exception as e:
            _logger.debug(f"Failed to create pipeline {extension.upper()} for {model_name}: {e}")
            return None

    def _get_sklearn_search_results_and_space_tables(self, model: ModelTypes, model_name: str) -> list[Table]:
        if not IS_PANDAS:
            _logger.debug("Pandas is not available, cannot process sklearn search results and space tables.")
            return []

        import pandas as pd

        tables = []
        results_df = pd.DataFrame(model.cv_results_)  # pyright: ignore

        try:
            tables.append(self._get_sklearn_search_space(model_name, results_df))
        except Exception as e:
            _logger.debug(f"Failed to get sklearn search space table for {model_name}: {e}")
        try:
            tables.append(self._get_sklearn_search_results(model_name, results_df))
        except Exception as e:
            _logger.debug(f"Failed to get sklearn search results table for {model_name}: {e}")
        return tables

    def _get_sklearn_search_results(self, model_name: str, results_df: DataFrame) -> Table:
        sorted_df = results_df.sort_values(by="rank_test_score")
        top_scores_df = sorted_df.head(5)
        return Table(top_scores_df, name=f"{model_name}_search_results")

    def _get_sklearn_search_space(self, model_name: str, results_df: DataFrame) -> Table:
        import pandas as pd

        param_columns = [col for col in results_df.columns if "param" in col and "params" not in col]
        data_dict = {}
        for param in param_columns:
            try:
                data_dict[f"{param} (min,max)"] = [[results_df[param].min(), results_df[param].max()]]
            except Exception:
                data_dict[f"{param} (uniques)"] = [results_df[param].unique()]

        params_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data_dict.items()]))
        # Transpose the DataFrame
        df_transposed = params_df.transpose()
        # Reset the index to move row headers into a column
        df_transposed_reset = df_transposed.reset_index()
        # Rename the index column for clarity
        df_transposed_reset = df_transposed_reset.rename(columns={"index": "Parameters", 0: "Values"})
        return Table(df_transposed_reset, name=f"{model_name}_search_space")
