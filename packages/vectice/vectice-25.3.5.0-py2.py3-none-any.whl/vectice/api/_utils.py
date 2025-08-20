from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectice.models.iteration import Iteration
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation


def read_nodejs_date(date_as_string: str | None) -> datetime | None:
    if date_as_string is None:
        return None
    return datetime.strptime(date_as_string, "%Y-%m-%dT%H:%M:%S.%f%z")


def get_asset_type(asset: DatasetVersionRepresentation | ModelVersionRepresentation | Iteration):
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    if isinstance(asset, DatasetVersionRepresentation):
        return "DATASET_VERSION"

    if isinstance(asset, ModelVersionRepresentation):
        return "MODEL_VERSION"

    return "ITERATION"


def get_asset_type_url(asset: DatasetVersionRepresentation | ModelVersionRepresentation | Iteration):
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    if isinstance(asset, DatasetVersionRepresentation):
        return "datasetversion"

    if isinstance(asset, ModelVersionRepresentation):
        return "modelversion"

    return "iteration"
