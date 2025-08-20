from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.api.json.iteration import IterationStepArtifact, IterationStepArtifactType
from vectice.models.representation.attachment import Attachment
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation
from vectice.utils.common_utils import repr_class

if TYPE_CHECKING:
    from vectice.api.client import Client


class IterationAssetRepresentation:
    """Represents an asset associated with an iteration.

    Attributes:
        section_name: The name of the section this asset belongs to.
            If not applicable, this can be None.
        index: The position or order of the asset within the section.
        type: The type of the asset, indicating
            whether it is a dataset version, model version, attachment, or comment.
        asset_id: A unique identifier for the asset.
        asset_name: The name of the asset. If the name is not available,
            this can be None.
    """

    from vectice.api.json.iteration import IterationStepArtifactType
    from vectice.models.representation.attachment import Attachment
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    section_name: str | None
    index: int
    type: str
    asset_id: int | str | None
    asset_name: str | None

    def __init__(self, output: IterationStepArtifact, client: Client) -> None:
        self._artifact_id = output.id
        self.section_name = output.section_name
        self.index = output.index
        self.type = output.type.value
        self.asset_id = output.asset_id
        self.asset_name = output.asset_name
        self._client = client
        self._text = output.text

    def __repr__(self):
        return repr_class(self)

    @property
    def asset(
        self,
    ) -> ModelVersionRepresentation | DatasetVersionRepresentation | Attachment | str | int | float | None:
        """The actual asset, which could be a model version, dataset version,
            attachment or a comment.

        Returns:
            ModelVersionRepresentation | DatasetVersionRepresentation | Attachment | str | int | float | None:
            The actual asset, or `None` if no asset is available.
        """
        if not self.asset_id:
            return self._text

        if isinstance(self.asset_id, str):
            if self.type == IterationStepArtifactType.ModelVersion.value:
                return ModelVersionRepresentation(self._client.get_model_version(self.asset_id), self._client)
            if self.type == IterationStepArtifactType.DataSetVersion.value:
                return DatasetVersionRepresentation(self._client.get_dataset_version(self.asset_id), self._client)
        elif self.asset_name:
            if self.type == IterationStepArtifactType.EntityFile.value:
                return Attachment(self.asset_id, self.asset_name, "file")

            return Attachment(self.asset_id, self.asset_name, "table")
