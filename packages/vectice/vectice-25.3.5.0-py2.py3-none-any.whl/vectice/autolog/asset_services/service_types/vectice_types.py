from __future__ import annotations

from enum import Enum


class VecticeType(Enum):
    MODEL = "MODEL"
    METRIC = "METRIC"
    DATASET = "DATASET"
    VECTICE_OBJECT = "VECTICE_OBJECT"
    IPYWIDGETS_OUTPUT = "IPYWIDGETS_OUTPUT"
