from __future__ import annotations

import logging

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata.base import DatasetSourceOrigin
from vectice.models.resource.metadata.dataframe_config import DataFrameType
from vectice.models.resource.metadata.db_metadata import DBMetadata, MetadataDB, TableType

_logger = logging.getLogger(__name__)

TDataFrameType = DataFrameType


class NoResource(Resource):
    """Wrap columnar data and its metadata in a local file.

    This resource wraps data that you have stored in a local file with optional metadata and versioning.
    You pass it as an argument of your Vectice Dataset wrapper before logging it to an iteration.

    ```python
    from vectice import FileResource

    resource = FileResource(paths="my/file/path")
    ```

    NOTE: **Vectice does not store your actual dataset. Instead, it stores your dataset's metadata, which is information about your dataset.
    These details are captured by resources tailored to the specific environment in use, such as: local (FileResource), Bigquery, S3, GCS...**
    """

    _origin = DatasetSourceOrigin.LOCAL.value

    def __init__(
        self,
        origin: str,
        dataframes: TDataFrameType | list[TDataFrameType] | None = None,
        capture_schema_only: bool = False,
        type: TableType = TableType.UNKNOWN,
        columns_description: dict[str, str] | None = None,
    ):
        """Initialize a file resource.

        Parameters:
            paths: The paths of the files to wrap.
            dataframes (Optional): The dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats. (Support Pandas, Spark)
            capture_schema_only (Optional): A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes.
            type (Optional): The resource type.

        Examples:
            The following example shows how to wrap a CSV file
            called `iris.csv` in the current directory:

            ```python
            from vectice import FileResource
            iris_trainset = FileResource(paths="iris.csv")
            ```
        """
        super().__init__(
            paths="",
            dataframes=dataframes,
            capture_schema_only=capture_schema_only,
            columns_description=columns_description,
        )
        self._origin = origin
        self._type = type

    def _fetch_data(
        self,
    ) -> dict:
        return {}

    def _build_metadata(self) -> DBMetadata:
        dbs = []
        if self._dataframes:
            for dataframe in self._dataframes:
                dbs.append(
                    MetadataDB(
                        name="Dataframe",
                        uri="Dataframe",
                        dataframe=dataframe,
                        display_name="Dataframe",
                        capture_schema_only=self.capture_schema_only,
                        columns=[],
                        type=self._type,
                    )
                )

            metadata = DBMetadata(
                size=0,
                origin=self._origin,
                dbs=dbs,
            )
            return metadata
        raise ValueError("A dataframe is required.")
