from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata import DatasetSourceOrigin
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.files_metadata import File, FilesMetadata

if TYPE_CHECKING:
    from google.cloud.storage import Blob, Client

GS_URI_REG = r"(gs:\/\/)([^\/]+)\/(.+)"

_logger = logging.getLogger(__name__)


TDataFrameType = DataFrameType


class GCSResource(Resource):
    """GCS resource reference wrapper.

    This resource wraps GCS uris references such as file folders that you have stored in Google Cloud
    Storage with optional metadata and versioning.
    You pass it as an argument of your Vectice Dataset wrapper before logging it to an iteration.


    ```python
    from vectice import GCSResource

    gcs_resource = GCSResource(
        uris="gs://<bucket_name>/<file_path_inside_bucket>",
    )
    ```

    NOTE: **Vectice does not store your actual dataset. Instead, it stores your dataset's metadata, which is information about your dataset.
    These details are captured by resources tailored to the specific environment in use, such as: local (FileResource), Bigquery, S3, GCS...**
    """

    _origin = DatasetSourceOrigin.GCS.value

    def __init__(
        self,
        uris: str | list[str],
        dataframes: TDataFrameType | list[TDataFrameType] | None = None,
        gcs_client: Client | None = None,
        capture_schema_only: bool = False,
        columns_description: dict[str, str] | str | None = None,
    ):
        """Initialize a GCS resource.

        Parameters:
            uris: The uris of the referenced resources. Should follow the pattern 'gs://<bucket_name>/<file_path_inside_bucket>'
            dataframes (Optional): The dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats. (Support Pandas, Spark, H2O)
            gcs_client (Optional): The `google.cloud.storage.Client` to optionally retrieve file size, creation date and updated date (used for auto-versioning) up to 5000 files.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            columns_description (Optional): A dictionary or path to a csv file to map the column's name to a specific description. Dictionary should follow the format { "column_name": "Description", ... }

        """
        super().__init__(
            paths=uris,
            dataframes=dataframes,
            capture_schema_only=capture_schema_only,
            columns_description=columns_description,
        )
        self.gcs_client = gcs_client

        for uri in self._paths:
            if not re.search(GS_URI_REG, uri):
                raise ValueError(
                    f"Uri '{uri}' is not following the right pattern 'gs://<bucket_name>/<file_path_inside_bucket>'"
                )

    def _fetch_data(self) -> dict[str, bytes | None]:
        datas = {}
        for uri in self._paths:
            bucket_name, path = self._get_bucket_and_path_from_uri(uri)
            blobs = self._get_blobs(bucket_name, path)
            if blobs is not None:
                for blob in blobs:
                    datas[f"{bucket_name}/{path}"] = blob
        return datas

    def _build_metadata(self) -> FilesMetadata:
        files = []
        size: int | None = None
        df_index = 0
        for uri in self._paths:
            bucket_name, path = self._get_bucket_and_path_from_uri(uri)
            blobs = self._get_blobs(bucket_name, path)
            if blobs is not None:
                sorted_blobs = sorted(blobs, key=lambda bl: str(bl.name).lower())
                for blob in sorted_blobs:
                    dataframe = (
                        self._dataframes[df_index]
                        if self._dataframes is not None and len(self._dataframes) > df_index
                        else None
                    )
                    blob_file = self._build_file_from_blob(blob, f"gs://{bucket_name}", dataframe)
                    files.append(blob_file)
                    if size is None and blob_file.size is not None:
                        size = 0
                    if size is not None:
                        size += blob_file.size or 0
                    df_index += 1
            else:
                dataframe = (
                    self._dataframes[df_index]
                    if self._dataframes is not None and len(self._dataframes) > df_index
                    else None
                )
                files.append(
                    File(
                        name=path,
                        uri=uri,
                        dataframe=dataframe,
                        display_name=path.rpartition("/")[-1],
                        capture_schema_only=self.capture_schema_only,
                    )
                )
                df_index += 1
        metadata = FilesMetadata(
            size=size,
            origin=self._origin,
            files=files,
        )
        return metadata

    def _get_blobs(self, bucket_name: str, path: str) -> list[Blob] | None:
        if self.gcs_client is None:
            return None

        blobs_list = list(
            filter(
                lambda bl: bl.name.endswith("/") is False,  # pyright: ignore[reportGeneralTypeIssues]
                self.gcs_client.list_blobs(
                    bucket_or_name=bucket_name, prefix=path, max_results=(self._files_limit + 2)
                ),  # +2 for base directory and to check if more files than limit
            )
        )

        if len(blobs_list) > self._files_limit:
            _logger.warning(f"Only first {self._files_limit} files metadata were used.")
            blobs_list.pop()

        return blobs_list

    def _build_file_from_blob(self, blob: Blob, uri: str, dataframe: TDataFrameType | None = None) -> File:
        name = blob.name
        if not isinstance(name, str):
            raise ValueError("Missing name in GCS data")

        return File(
            name=name,
            size=blob.size,
            fingerprint=blob.md5_hash,
            created_date=blob.time_created.isoformat() if blob.time_created is not None else None,
            updated_date=blob.updated.isoformat() if blob.updated is not None else None,
            uri=f"{uri}/{name}",
            dataframe=dataframe,
            content_type=blob.content_type,
            display_name=name.rpartition("/")[-1],
            capture_schema_only=self.capture_schema_only,
        )

    def _get_bucket_and_path_from_uri(self, uri: str) -> tuple[str, str]:
        match = re.search(GS_URI_REG, uri)
        if match is not None:
            _, bucket_name, path = match.groups()
            return bucket_name, path

        raise ValueError(
            f"Uri '{uri}' is not following the right pattern 'gs://<bucket_name>/<file_path_inside_bucket>'"
        )


class NoSuchGCSResourceError(Exception):
    def __init__(self, bucket: str, resource: str):
        self.message = f"{resource} does not exist in the GCS bucket {bucket}."
        super().__init__(self.message)
