from __future__ import annotations

import logging
import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, List, TypedDict

from vectice.models.table import Table

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from numpy.typing import ArrayLike
    from pandas import DataFrame


class ValidationType(Enum):
    """Enumeration of the supported types for validation class."""

    BinaryClassification = "BinaryClassification"


MAP_TYPE = {
    ValidationType.BinaryClassification: ["roc", "cm", "binary_full_suite", "explainability", "feature_importance"]
}


def aggregate_dict(dict1: TestSuiteReturnType, dict2: TestSuiteReturnType) -> TestSuiteReturnType:
    for key, value in dict2["metrics"].items():
        dict1["metrics"][key] = value
    for key, value in dict2["properties"].items():
        dict1["properties"][key] = value

    dict1["tables"].extend(dict2["tables"])
    dict1["attachments"].extend(dict2["attachments"])

    return dict1


class TestSuiteReturnType(TypedDict):
    metrics: dict[str, Any]
    properties: dict[str, Any]
    tables: list[Table]
    attachments: list[str]


class ValidationModel:
    """Represent a validation suite of test to be run."""

    def __init__(
        self,
        asset: str | None,
        training_df: DataFrame,
        testing_df: DataFrame,
        target_column: str,
        predictor: Any,
        predict_proba_test: ArrayLike,
        predict_proba_train: ArrayLike | None = None,
        threshold: float = 0.5,
        type: ValidationType = ValidationType.BinaryClassification,
        tests: List[str | Callable[[Any], TestSuiteReturnType]] = ["roc", "cm"],
    ):
        if asset is None:
            warnings.warn("Asset is None, generated tests will be logged at iteration level.")

        mapped_type = MAP_TYPE[type]
        for test in tests:
            if test not in mapped_type:
                raise ValueError(f"Type {type} is incompatible with test {test}")

        self.asset = asset
        self._training_df = training_df
        self._testing_df = testing_df
        self._predictor = predictor
        self._type = type
        self._predict_proba_train = predict_proba_train
        self._predict_proba_test = predict_proba_test
        self._target = target_column
        self._threshold = threshold
        self._tests = tests

    def execute_test(self) -> TestSuiteReturnType:
        from vectice.models.test_library.binary_classification_test import MAP_TEST

        test_result: TestSuiteReturnType = {
            "metrics": {},
            "properties": {},
            "tables": [],
            "attachments": [],
        }
        for test in self._tests:
            if test in MAP_TEST:
                test_function = MAP_TEST[test]
                if isinstance(test_function, list):
                    for test_func in test_function:
                        temp_return = test_func(
                            self._training_df,
                            self._testing_df,
                            self._target,
                            self._predictor,
                            self._predict_proba_train,
                            self._predict_proba_test,
                            self._threshold,
                        )
                        test_result = aggregate_dict(test_result, temp_return)
                else:
                    temp_return = test_function(
                        self._training_df,
                        self._testing_df,
                        self._target,
                        self._predictor,
                        self._predict_proba_train,
                        self._predict_proba_test,
                        self._threshold,
                    )
                    test_result = aggregate_dict(test_result, temp_return)
            _logger.info(f"Test: {test} successfully run")
            # todo callable
        return test_result
