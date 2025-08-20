from __future__ import annotations

from typing import TypedDict, TypeVar

from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.models.dataset import Dataset
from vectice.models.model import Model
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_representation import ModelRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation
from vectice.models.table import Table
from vectice.models.validation import ValidationModel

VecticeObjectTypes = TypeVar(
    "VecticeObjectTypes",
    Dataset,
    Model,
    Table,
    ValidationModel,
    DatasetVersionRepresentation,
    ModelVersionRepresentation,
    ModelRepresentation,
    DatasetRepresentation,
)
TVecticeObjects = TypedDict(
    "TVecticeObjects", {"variable": str, "vectice_object": VecticeObjectTypes, "asset_type": VecticeType}
)
VecticeObjectClasses = (
    Dataset,
    Model,
    Table,
    ValidationModel,
    DatasetVersionRepresentation,
    ModelVersionRepresentation,
    ModelRepresentation,
    DatasetRepresentation,
)


class AutologVecticeAssetService:
    def __init__(self, key: str, asset: VecticeObjectTypes):
        self._asset = asset
        self._key = key

    def get_asset(self):
        return {"variable": self._key, "vectice_object": self._asset, "asset_type": VecticeType.VECTICE_OBJECT}
