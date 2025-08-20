from enum import Enum


class ModelLibrary(Enum):
    """Enumeration that defines what the model library."""

    SKLEARN = "SKLEARN"
    SKLEARN_PIPELINE = "SKLEARN_PIPELINE"
    SKLEARN_SEARCH = "SKLEARN_SEARCH"
    LIGHTGBM = "LIGHTGBM"
    CATBOOST = "CATBOOST"
    KERAS = "KERAS"
    STATSMODEL = "STATSMODEL"
    PYTORCH = "PYTORCH"
    PYSPARKML = "PYSPARKML"
    H2O = "H2O"
    NONE = "NONE"
