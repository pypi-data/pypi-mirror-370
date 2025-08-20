from __future__ import annotations

import io
import logging
import os
from functools import reduce
from typing import TYPE_CHECKING, BinaryIO, List

from vectice.api.json.model_version import ModelVersionOutput
from vectice.models.attachment import TFormattedAttachment
from vectice.models.table import Table
from vectice.types.version import TVersion
from vectice.utils.common_utils import capture_unique_attachments

if TYPE_CHECKING:
    from vectice.api import Client

_logger = logging.getLogger(__name__)

FILE_PATH_DOES_NOT_EXIST_ERROR_MESSAGE = "The file path '%s' is not valid. The file does not exist."


class AttachmentContainer:
    def __init__(self, version: TVersion, client: Client):
        self._client = client
        self._version = version
        self._id = version.id
        self._name = version.name

    @property
    def version(self):
        return self._version

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def upsert_attachments(self, attachments: list[TFormattedAttachment]):
        """Add an attachment or set of attachments to the entity.

        Parameters:
            attachments: The paths of the attachment(s).

        Returns:
            A list of dictionaries describing the attachments.
        """

        def _upsert_files(files: list[str]) -> list[str]:
            if len(files) > 0:
                files_attachments = self._add_files_to_attachments(files)
                try:
                    return list(
                        map(
                            lambda curr: curr.fileName,
                            self._client.upsert_version_attachments(files_attachments, self._version),
                        )
                    )
                finally:
                    self._close_attached_files(files_attachments)
            return []

        def _upsert_tables(tables: list[Table]) -> list[str]:
            return (
                list(map(lambda curr: curr["name"], self._client.upsert_version_tables(tables, self._version)))
                if len(tables) > 0
                else []
            )

        files, tables = reduce(capture_unique_attachments, attachments, ([], []))
        return [*_upsert_files(files), *_upsert_tables(tables)]

    def _add_files_to_attachments(self, file_paths: list[str]) -> list[tuple[str, tuple[str, BinaryIO]]]:
        attachments: List[tuple[str, tuple[str, BinaryIO]]] = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise ValueError(FILE_PATH_DOES_NOT_EXIST_ERROR_MESSAGE % file_path)
            curr_file = ("file", (file_path, open(file_path, "rb")))
            attachments.append(curr_file)
        return attachments

    def _close_attached_files(self, attachments: list[tuple[str, tuple[str, BinaryIO]]]) -> None:
        for attachment in attachments:
            attachment[1][1].close()

    def add_serialized_model(self, model_type: str, model_content: bytes):
        if isinstance(self._version, ModelVersionOutput):
            self._client.create_model_predictor(model_type, io.BytesIO(model_content), self._version)
