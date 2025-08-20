from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:

    from catboost.core import CatBoost
    from keras import Model as KerasModel  # type: ignore[reportMissingImports]  # type: ignore[reportMissingImports]
    from keras.models import Model as KerasModel  # type: ignore[reportMissingImports]
    from lightgbm.basic import Booster
    from sklearn.base import BaseEstimator
    from sklearn.pipeline import Pipeline
    from torch.nn import Module as TorchModel

    ModelTypes = TypeVar("ModelTypes", BaseEstimator, Booster, CatBoost, KerasModel, TorchModel, Pipeline)
