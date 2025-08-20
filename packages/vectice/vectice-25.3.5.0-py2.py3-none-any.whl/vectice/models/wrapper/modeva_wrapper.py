from __future__ import annotations

from importlib.util import find_spec
from typing import Any

from modeva import DataSet, FactSheet  # pyright: ignore[reportMissingImports]
from modeva.models.wrappers.api import (  # pyright: ignore[reportMissingImports]
    modeva_arbitrary_classifier,
    modeva_arbitrary_regressor,
    modeva_sklearn_classifier,
    modeva_sklearn_regressor,
)
from modeva.utils.results import ValidationResult  # type: ignore[reportMissingImports]
from pandas import DataFrame

SKLEARN_MODEL_WRAPPERS = [modeva_sklearn_classifier, modeva_sklearn_regressor]
ARBITARY_MODEL_WRAPPERS = [modeva_arbitrary_classifier, modeva_arbitrary_regressor]

is_selenium = find_spec("selenium") is not None
if is_selenium:
    from functools import wraps

    from selenium.webdriver.chrome.options import Options  # type: ignore[reportMissingImports]

    original_add_argument = Options.add_argument

    def add_argument_with_extras(func):  # type: ignore[reportMissingParameterType]
        @wraps(func)
        def wrapper(self, argument):  # type: ignore[reportMissingParameterType]
            # call the original method
            result = func(self, argument)
            # add extra options
            func(self, "--disable-dev-shm-usage")
            func(self, "--disable-gpu")
            func(self, "--headless")
            func(self, "--no-sandbox")
            return result

        return wrapper

    Options.add_argument = add_argument_with_extras(Options.add_argument)


def modeva_wrapper(
    dataset_train: DataFrame,
    dataset_test: DataFrame,
    main_model: Any | None = None,
    comparison_models: list | None = None,
    dataset_out: DataFrame | None = None,
    target: str | None = None,
) -> FactSheet:
    """Wraps the input datasets and models into a Vectice fact sheet.
       You can pass either a main_model or comparison_models.

    Args:
        dataset_train (DataFrame): The training dataset used for model evaluation.
        dataset_test (DataFrame): The test dataset used for model evaluation.
        main_model (Any): The main model to be evaluated.
        comparison_models (list): A list of models to be evaluated.
        dataset_out (DataFrame, optional): An optional out of time dataset. Defaults to None.
        target (str, optional): The target column of the dataset_train provided. Defaults to the last column.

    Returns:
        FactSheet: A fact sheet object that contains details about the datasets and models.
    """
    fact_sheet = VecticeFactSheet(dataset_train, dataset_test, main_model, comparison_models, dataset_out, target)
    return fact_sheet


class VecticeFactSheet(FactSheet):  # type: ignore[reportUntypedBaseClass]
    def __init__(
        self,
        dataset_train: DataFrame,
        dataset_test: DataFrame,
        main_model: Any | None = None,
        comparison_models: list | None = None,
        dataset_out: DataFrame | None = None,
        target: str | None = None,
    ):
        self._dataset = self._dataset_setup(dataset_train, dataset_test, dataset_out, target)
        if not comparison_models:
            self._main_model = self._get_sklearn_model(main_model) or self._get_arbitrary_model(main_model)
        else:
            self._main_model = None
        self._comparison_models = self._models_setup(comparison_models) if comparison_models else None
        self._validation_test_results: list[ValidationResult] | list = []

        super().__init__(self._dataset, self._main_model, self._comparison_models)

    def run_robustness_test_suite(self):
        from tqdm.notebook import tqdm  # pyright: ignore[reportMissingImports]

        # robustness_tests = [self.explain_shap, self.diagnose_accuracy_table, self.diagnose_robustness, self.diagnose_reliability, self.diagnose_resilience]
        robustness_tests = [self.explain_shap, self.diagnose_accuracy_table, self.diagnose_resilience]

        with tqdm(robustness_tests) as pbar:
            for test in robustness_tests:
                pbar.set_description(f"Test Suite {test.__name__} running")
                result = test()
                pbar.update(1)
                self._validation_test_results.append(result)

    def _get_arbitrary_model(self, model: Any):
        # try arb
        for wrapper in ARBITARY_MODEL_WRAPPERS:
            algorithmn_name = str(model.__class__).split(".")[-1]
            algorithmn_name = algorithmn_name.replace("'>", "")
            try:
                # regressor / params are for regression models
                wrapped = wrapper(name=algorithmn_name, predict_function=model.predict, fit_function=model.fit)
                self._dataset.set_task_type("Regression")
                return wrapped
            except Exception:
                pass
            try:
                # classifier / params are for classification models
                wrapped = wrapper(
                    name=algorithmn_name,
                    predict_function=model.predict,
                    predict_proba_function=model.predict_proba,
                    fit_function=model.fit,
                )
                self._dataset.set_task_type("Classification")
                return wrapped
            except Exception:
                pass

    def _get_sklearn_model(self, model: Any):
        from sklearn.base import is_classifier, is_regressor

        for wrapper in SKLEARN_MODEL_WRAPPERS:
            algorithmn_name = str(model.__class__).split(".")[-1]
            algorithmn_name = algorithmn_name.replace("'>", "")
            try:
                wrapped = wrapper(name=algorithmn_name, estimator=model)
                if is_regressor(model):
                    self._dataset.set_task_type("Regression")
                if is_classifier(model):
                    self._dataset.set_task_type("Classification")
                return wrapped
            except Exception:
                pass

    def _models_setup(self, models: list) -> list:
        # converts estimators to modeva wrapped models
        wrapped_models = []
        for model in models:
            # modeva wrappers seem to generalize well for the following
            # sklearn, xgboost, lightgbm and catboost
            wrapped_model = self._get_sklearn_model(model) or self._get_arbitrary_model(model)
            if wrapped_model:
                wrapped_models.append(wrapped_model)
        return wrapped_models

    def _dataset_setup(
        self,
        dataset_train: DataFrame,
        dataset_test: DataFrame,
        dataset_out: DataFrame | None = None,
        target: str | None = None,
    ) -> DataSet:
        # TODO series data / numpy arrays
        # takes train & test and creates a modeva DataSet
        dataset = DataSet()
        dataset.load_dataframe_train_test(train=dataset_train, test=dataset_test)
        if dataset_out is not None:
            dataset.set_raw_extra_data(name="oot", data=dataset_out)
        # TODO add a target parameter
        # assume initially
        if target is None:
            target = dataset_train.columns[-1]
        dataset.set_target(target)
        return dataset
