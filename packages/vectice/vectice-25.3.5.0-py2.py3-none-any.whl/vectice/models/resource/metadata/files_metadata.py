from __future__ import annotations

from vectice.models.resource.metadata.base import (
    DatasetSourceType,
    DatasetSourceUsage,
    Metadata,
)
from vectice.models.resource.metadata.column_metadata import Column
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.extra_metadata import ExtraMetadata
from vectice.models.resource.metadata.source import Source


class FilesMetadata(Metadata):
    """The metadata of a set of files."""

    def __init__(
        self,
        files: list[File],
        size: int | None = None,
        usage: DatasetSourceUsage | None = None,
        origin: str | None = None,
    ):
        """Initialize a FilesMetadata instance.

        Parameters:
            files: The list of files of the dataset.
            size: The size of the set of files.
            usage: The usage of the dataset.
            origin: Where the dataset files come from.
        """
        super().__init__(size=size, type=DatasetSourceType.FILES, origin=origin, usage=usage)
        self.files = files

    def asdict(self) -> dict:
        for file in self.files:
            if self._settings is not None:  # pyright: ignore[reportUnnecessaryComparison]
                file.set_settings(self._settings)
        return {
            **super().asdict(),
            "files": [file.asdict() for file in self.files],
        }


TDataFrameType = DataFrameType


class File(Source):
    """Describe a dataset file."""

    def __init__(
        self,
        name: str,
        size: int | None = None,
        fingerprint: str | None = None,
        created_date: str | None = None,
        updated_date: str | None = None,
        uri: str | None = None,
        columns: list[Column] | None = None,
        dataframe: TDataFrameType | None = None,
        content_type: str | None = None,
        extra_metadata: list[ExtraMetadata] | None = None,
        display_name: str | None = None,
        capture_schema_only: bool = False,
    ):
        """Initialize a file.

        Parameters:
            name: The name of the file.
            size: The size of the file.
            fingerprint: The hash of the file.
            created_date: The date of creation of the file.
            updated_date: The date of last update of the file.
            uri: The uri of the file.
            columns: The columns coming from the dataframe with the statistics.
            dataframe (Optional): A dataframe allowing vectice to optionally compute more metadata about this resource such as columns stats, size, rows number and column numbers. (Support Pandas and Spark)
            content_type (Optional): HTTP 'Content-Type' header for this file.
            extra_metadata (Optional): Extra metadata to be captured.
            display_name (Optional): Name that will be shown in the Web App.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.

        """
        super().__init__(
            name=name,
            size=size,
            columns=columns,
            created_date=created_date,
            updated_date=updated_date,
            uri=uri,
            dataframe=dataframe,
            extra_metadata=extra_metadata,
            display_name=display_name,
            capture_schema_only=capture_schema_only,
        )
        self.fingerprint = fingerprint
        self.content_type = content_type

    def asdict(self) -> dict:
        return {
            **super().asdict(),
            "fingerprint": self.fingerprint,
            "createdDate": self.created_date,
            "mimeType": self.content_type,
            "filename": self.display_name,
        }
