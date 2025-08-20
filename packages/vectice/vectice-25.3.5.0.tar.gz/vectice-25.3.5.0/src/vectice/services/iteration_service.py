from __future__ import annotations

import logging
from io import BufferedReader, IOBase
from textwrap import dedent
from typing import TYPE_CHECKING

from PIL.Image import Image

from vectice.api.http_error_handlers import ArtifactVersionIdExistingError, VecticeException
from vectice.api.json import DatasetRegisterOutput, EntityFileOutput, ModelRegisterOutput
from vectice.api.json.iteration import (
    IterationStepArtifactEntityMetadataInput,
    IterationStepArtifactInput,
    IterationStepArtifactType,
    IterationUpdateInput,
)
from vectice.utils.common_utils import (
    check_string_sanity,
    get_image_or_file_variables,
    get_notebook_path,
    get_script_path,
    set_dataset_attachments,
    set_model_attachments,
)
from vectice.utils.dataframe_utils import transform_table_to_metadata_dict

if TYPE_CHECKING:
    from vectice.api.client import Client
    from vectice.api.json.code_version import CodeVersion
    from vectice.models.dataset import Dataset
    from vectice.models.iteration import Iteration
    from vectice.models.model import Model
    from vectice.models.representation.dataset_representation import DatasetRepresentation
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_representation import ModelRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation
    from vectice.models.table import Table

    TAssetType = ModelRepresentation | ModelVersionRepresentation | DatasetRepresentation | DatasetVersionRepresentation

_logger = logging.getLogger(__name__)

lineage_file_id = None
code_source_file = get_notebook_path() or get_script_path()


class IterationService:
    def __init__(self, iteration: Iteration, client: Client):
        self._client = client
        self._iteration = iteration

    def log_image_or_file(self, asset: str | IOBase | Image, section: str | None = None):
        _, filename = self._create_image_or_file_artifact(asset, section)
        return filename

    def log_comment(self, asset: int | float | str, section: str | None = None):
        if isinstance(asset, str):
            check_string_sanity(asset)
        artifact_inp: list[IterationStepArtifactInput] = [IterationStepArtifactInput(type="Comment", text=str(asset))]
        self._client.add_iteration_artifacts(iteration_id=self._iteration.id, artifacts=artifact_inp, section=section)

    def log_table(self, asset: Table, section: str | None = None):
        data = transform_table_to_metadata_dict(asset)
        entity_metadata = IterationStepArtifactEntityMetadataInput(name=asset.name, content={"data": data})

        artifact_inp: list[IterationStepArtifactInput] = [
            IterationStepArtifactInput(type="EntityMetadata", entityMetadata=entity_metadata)
        ]
        self._client.add_iteration_artifacts(iteration_id=self._iteration.id, artifacts=artifact_inp, section=section)

    def log_model(self, asset: Model, section: str | None = None):
        from vectice import code_file_capture

        global code_source_file

        code_version = self._get_code_version()
        model_data = self._client.register_model(
            model=asset,
            phase=self._iteration.phase,
            iteration=self._iteration,
            code_version=code_version,
            section=section,
        )
        if code_file_capture:
            if code_source_file:
                self._attach_code_file_to_lineage(model_data, code_source_file)
        attachments_output, success_pickle = set_model_attachments(self._client, asset, model_data.model_version)
        return model_data, attachments_output, success_pickle

    def log_dataset(self, asset: Dataset, section: str | None = None):
        from vectice import code_file_capture

        global code_source_file

        code_version = self._get_code_version()
        dataset_output = self._client.register_dataset_from_source(
            dataset=asset,
            iteration_id=self._iteration.id,
            code_version=code_version,
            section=section,
        )
        if code_file_capture:
            if code_source_file:
                self._attach_code_file_to_lineage(dataset_output, code_source_file)
        attachments_output = set_dataset_attachments(self._client, asset, dataset_output.dataset_version)
        return dataset_output, attachments_output

    def assign_version_representation(
        self,
        asset: TAssetType,
        section: str | None = None,
    ) -> tuple[str, bool]:
        from vectice.models.representation.dataset_representation import DatasetRepresentation
        from vectice.models.representation.model_representation import ModelRepresentation

        asset_type = self._get_asset_type_from_asset_representation(asset)

        is_parent = isinstance(asset, (ModelRepresentation, DatasetRepresentation))
        asset_id = self._get_last_version_id(asset) if is_parent else asset.id
        artifact_inp = [
            IterationStepArtifactInput(
                type=asset_type,
                id=asset_id,
            )
        ]
        already_assigned: bool = False
        try:
            self._client.add_iteration_artifacts(
                iteration_id=self._iteration.id, artifacts=artifact_inp, section=section
            )
        except ArtifactVersionIdExistingError:
            already_assigned = True

        return asset_type, already_assigned

    def save_autolog_assets(self, cells: list[dict[str, str]], prefix: str | None = None, is_trace: bool = False):
        self._client.save_autolog_cells(self._iteration.id, cells, prefix, is_trace)

    def organize_with_ai(self):
        self._client.organize_with_ai(self._iteration.id)

    def organize_with_ai_and_report(self):
        report_data = self._client.organize_with_ai_and_report(self._iteration.id)
        hyper_link = f"{self._client.auth.api_base_url}/project/{self._iteration.phase.project.id}/reports"
        logging_output = dedent(
            f"""
                The report '{report_data.name}' is currently being generated and will be accessible via this link in a few minutes:
                {hyper_link}
            """
        ).lstrip()

        _logger.info(logging_output)

    def _get_asset_type_from_asset_representation(
        self,
        asset: TAssetType,
    ):
        from vectice.models.representation.dataset_representation import DatasetRepresentation
        from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
        from vectice.models.representation.model_representation import ModelRepresentation
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        if isinstance(asset, (ModelRepresentation, ModelVersionRepresentation)):
            return "ModelVersion"
        if isinstance(
            asset, (DatasetRepresentation, DatasetVersionRepresentation)
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            return "DataSetVersion"

        raise ValueError(f"Asset type '{type(asset)!s}' is unsupported")

    def _get_last_version_id(self, value: ModelRepresentation | DatasetRepresentation):
        last_version = value._last_version  # pyright: ignore [reportPrivateUsage]
        if last_version is None:
            raise VecticeException("Unable to log asset, no versions exist.")
        return last_version.id

    def update(self, name: str | None = None, description: str | None = None):
        if name is None and description is None:
            return

        self._client.update_iteration(self._iteration.id, IterationUpdateInput(name=name, description=description))
        if name is not None:
            self._iteration.name = name

        self._iteration.description = description
        _logger.info(f"Iteration {self._iteration.id!r} successfully updated.")

    def _create_code_version_file_artifact(
        self, value: str | IOBase | Image, lineage_id: int
    ) -> EntityFileOutput | None:
        is_image_or_file, filename = get_image_or_file_variables(value)
        try:
            artifact, *_ = self._client.upsert_lineage_attachments(
                files=[("file", (filename, is_image_or_file))], lineage_id=lineage_id
            )
            if isinstance(is_image_or_file, BufferedReader):
                is_image_or_file.close()
            return EntityFileOutput(
                fileId=artifact.fileId,
                fileName=artifact.fileName,
                contentType=artifact.contentType,
                entityId=artifact.entityId,
                entityType=artifact.entityType,
            )
        except VecticeException as error:
            raise error
        except Exception:
            pass

    def _create_image_or_file_artifact(
        self, value: str | IOBase | Image, section: str | None = None
    ) -> tuple[IterationStepArtifactInput, str]:
        is_image_or_file, filename = get_image_or_file_variables(value)
        try:
            artifact, *_ = self._client.upsert_iteration_attachments(
                files=[("file", (filename, is_image_or_file))], iteration_id=self._iteration.id, step_name=section
            )
            if isinstance(is_image_or_file, BufferedReader):
                is_image_or_file.close()
            return (
                IterationStepArtifactInput(id=artifact.fileId, type=IterationStepArtifactType.EntityFile.name),
                filename,
            )
        except VecticeException as error:
            raise error
        except Exception as error:
            raise ValueError("Check the provided image.") from error

    def _get_code_version(self) -> CodeVersion | None:
        # TODO: cyclic imports
        from vectice import code_capture
        from vectice.models.code_version import capture_code_version, inform_if_git_repo

        if code_capture:
            return capture_code_version()
        else:
            inform_if_git_repo()
            return None

    def _attach_code_file_to_lineage(
        self, asset_output: DatasetRegisterOutput | ModelRegisterOutput, code_source_file: str
    ) -> None:
        global lineage_file_id

        try:
            lineage_id = None
            if hasattr(asset_output, "dataset_version"):
                lineage_id = asset_output.dataset_version.origin_id  # pyright: ignore[reportAttributeAccessIssue]
            if hasattr(asset_output, "model_version"):
                lineage_id = asset_output.model_version.origin_id  # pyright: ignore[reportAttributeAccessIssue]

            if lineage_id and lineage_file_id:
                self._client.attach_file_to_lineage(lineage_id, lineage_file_id)
            if lineage_id and lineage_file_id is None:
                attachment_output = self._create_code_version_file_artifact(code_source_file, lineage_id)
                lineage_file_id = attachment_output.fileId if attachment_output else None
        except Exception:
            pass
