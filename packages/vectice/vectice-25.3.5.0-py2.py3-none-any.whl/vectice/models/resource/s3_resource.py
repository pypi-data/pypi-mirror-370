from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata.base import DatasetSourceOrigin
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.files_metadata import File, FilesMetadata

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client as Client
    from mypy_boto3_s3.type_defs import ListObjectsV2OutputTypeDef, ObjectTypeDef


S3_URI_REG = r"(s3:\/\/)([^\/]+)\/(.+)"


_logger = logging.getLogger(__name__)

TDataFrameType = DataFrameType


class S3Resource(Resource):
    """AWS S3resource reference wrapper.

    This resource wraps AWS S3 uris references such as file folders that you have stored in AWS S3
    with optional metadata and versioning.
    You pass it as an argument of your Vectice Dataset wrapper before logging it to an iteration.


    ```python
    from vectice import S3Resource

    s3_resource = S3Resource(
        uris="s3://<bucket_name>/<file_path_inside_bucket>",
    )
    ```

    NOTE: **Vectice does not store your actual dataset. Instead, it stores your dataset's metadata, which is information about your dataset.
    These details are captured by resources tailored to the specific environment in use, such as: local (FileResource), Bigquery, S3, GCS...**

    """

    _origin = DatasetSourceOrigin.S3.value

    def __init__(
        self,
        uris: str | list[str],
        dataframes: TDataFrameType | list[TDataFrameType] | None = None,
        s3_client: Client | None = None,
        capture_schema_only: bool = False,
        columns_description: dict[str, str] | str | None = None,
    ):
        """Initialize an S3 resource.

        Parameters:
            uris: The uris of the resources to get. Should follow the pattern 's3://<bucket_name>/<file_path_inside_bucket>'
            dataframes (Optional): The dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats. (Support Pandas, Spark, H2O)
            s3_client (Optional): The Amazon s3 client to optionally retrieve file size, creation date and updated date (used for auto-versioning) up to 5000 files.
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            columns_description (Optional): A dictionary or path to a csv file to map the column's name to a specific description. Dictionary should follow the format { "column_name": "Description", ... }

        """
        super().__init__(
            paths=uris,
            dataframes=dataframes,
            capture_schema_only=capture_schema_only,
            columns_description=columns_description,
        )
        self.s3_client = s3_client
        for uri in self._paths:
            if not re.search(S3_URI_REG, uri):
                raise ValueError(
                    f"Uri '{uri}' is not following the right pattern 's3://<bucket_name>/<file_path_inside_bucket>'"
                )

    def _fetch_data(self) -> dict[str, ObjectTypeDef | None]:
        datas: dict[str, ObjectTypeDef | None] = {}
        if self.s3_client:
            for bucket_name, s3_objects_list in self._get_s3_objects_list(self.s3_client):
                for s3_objects in s3_objects_list:
                    for s3_object in s3_objects["Contents"]:
                        object_path = s3_object.get("Key")
                        datas[f"{bucket_name}/{object_path}"] = s3_object
        else:
            for path in self._paths:
                datas[path] = None

        return datas

    def _build_metadata(self) -> FilesMetadata:
        size = None
        files = []
        df_index = 0
        if self.s3_client:
            for bucket_name, s3_objects_list in self._get_s3_objects_list(self.s3_client):
                for s3_objects in s3_objects_list:
                    if s3_objects["KeyCount"] == 0:
                        raise NoSuchS3ResourceError(bucket_name, s3_objects["Prefix"])
                    s3_object = s3_objects["Contents"]
                    new_files, total_size, new_df_index = self._build_files_list_with_size(
                        index=df_index, bucket_name=bucket_name, s3_object=s3_object
                    )
                    if size is None:
                        size = 0
                    size += total_size
                    files.extend(new_files)
                    df_index += new_df_index
        else:
            for index, uri in enumerate(self._paths):
                dataframe = (
                    self._dataframes[index] if self._dataframes is not None and len(self._dataframes) > index else None
                )
                _, path = self._get_bucket_and_path_from_uri(uri)
                file = File(
                    name=path,
                    uri=uri,
                    dataframe=dataframe,
                    display_name=path.rpartition("/")[-1],
                    capture_schema_only=self.capture_schema_only,
                )
                files.append(file)

        metadata = FilesMetadata(files=files, origin=self._origin, size=size)
        return metadata

    def _build_files_list_with_size(
        self, index: int, bucket_name: str, s3_object: list[ObjectTypeDef]
    ) -> tuple[list[File], int, int]:
        files: list[File] = []
        total_size = 0
        df_index = 0
        filtered_s3_object = list(filter(lambda obj: self._is_s3_object_a_folder(obj) is False, s3_object))
        sorted_s3_object = sorted(filtered_s3_object, key=lambda obj: obj.get("Key").lower())  # type: ignore
        for object in sorted_s3_object:
            new_index = df_index + index
            key = object.get("Key")
            name = key if key is not None else "Unknown"
            size = object.get("Size")
            uri = f"s3://{bucket_name}/{name}"
            dataframe = (
                self._dataframes[new_index]
                if self._dataframes is not None and len(self._dataframes) > new_index
                else None
            )

            file = File(
                name=name,
                size=size,
                fingerprint=self._get_formatted_etag_from_object(object),
                updated_date=object.get("LastModified").isoformat(),  # type: ignore
                created_date=None,
                uri=uri,
                dataframe=dataframe,
                display_name=name.rpartition("/")[-1],  # type: ignore
                capture_schema_only=self.capture_schema_only,
            )
            if size is not None:
                total_size += size
            files.append(file)
            df_index += 1
        return files, total_size, df_index

    def _get_s3_objects_list(self, s3_client: Client) -> list[tuple[str, list[ListObjectsV2OutputTypeDef]]]:
        return list(map(lambda uri: self._get_s3_objects(s3_client, uri), self._paths))

    def _get_s3_objects(self, s3_client: Client, uri: str) -> tuple[str, list[ListObjectsV2OutputTypeDef]]:
        bucket_name, path = self._get_bucket_and_path_from_uri(uri)
        results: list[ListObjectsV2OutputTypeDef] = []
        next_token: str | None = ""
        base_kwargs = {
            "Bucket": bucket_name,
            "Prefix": path,
        }
        count = 0
        while next_token is not None:
            kwargs = base_kwargs.copy()
            if next_token != "":
                kwargs.update({"ContinuationToken": next_token})

            result = s3_client.list_objects_v2(**kwargs)  # type: ignore[arg-type]
            count += result["KeyCount"]
            if count >= self._files_limit:
                _logger.warning(f"Only first {self._files_limit} files metadata were used.")
                next_token = None
            else:
                next_token = result.get("NextContinuationToken")

            results.append(result)

        return bucket_name, results

    def _get_bucket_and_path_from_uri(self, uri: str) -> tuple[str, str]:
        match = re.search(S3_URI_REG, uri)
        if match is not None:
            _, bucket_name, path = match.groups()
            return bucket_name, path

        raise ValueError(
            f"Uri '{uri}' is not following the right pattern 's3://<bucket_name>/<file_path_inside_bucket>'"
        )

    @staticmethod
    def _get_formatted_etag_from_object(object: ObjectTypeDef) -> str:
        etag = object.get("ETag")
        return str(etag.replace("'", "").replace('"', "")) if etag else ""

    @staticmethod
    def _is_s3_object_a_folder(object: ObjectTypeDef) -> bool:
        key = object.get("Key")
        return bool(key.endswith("/")) if key else False


class NoSuchS3ResourceError(Exception):
    def __init__(self, bucket: str, resource: str):
        self.message = f"{resource} does not exist in the AWS s3 bucket {bucket}."
        super().__init__(self.message)
