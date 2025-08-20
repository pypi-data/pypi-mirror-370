from __future__ import annotations

from typing import Union

from vectice.api.json.dataset_version import DatasetVersionOutput
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.model_version import ModelVersionOutput
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput

TModelVersion = Union[ModelVersionOutput, ModelVersionRepresentationOutput]
TDatasetVersion = Union[DatasetVersionOutput, DatasetVersionRepresentationOutput]
TVersion = Union[TModelVersion, TDatasetVersion]

ModelVersionClasses = (ModelVersionOutput, ModelVersionRepresentationOutput)
DatasetVersionClasses = (DatasetVersionOutput, DatasetVersionRepresentationOutput)
