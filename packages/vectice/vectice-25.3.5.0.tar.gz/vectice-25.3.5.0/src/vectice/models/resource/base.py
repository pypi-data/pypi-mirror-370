from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from typing_extensions import get_args

from vectice.models.resource.metadata.base import DatasetSourceOrigin, Metadata
from vectice.models.resource.metadata.dataframe_config import DataFrameType

if TYPE_CHECKING:
    from vectice.models.resource.metadata.base import DatasetSourceUsage

TDataFrameType = DataFrameType


class Resource(metaclass=ABCMeta):
    """Base class for resources.

    Use Resource subclasses to assign datasets to steps.  The
    Vectice library supports a handful of common cases.  Additional
    cases are generally easy to supply by deriving from this base
    class.  In particular, subclasses must override this class'
    abstact methods (`_build_metadata()`, `_fetch_data()`).

    Examples:
        To create a custom resource class, inherit from `Resource`,
        and implement the `_build_metadata()` and `_fetch_data()` methods:

        ```python
        from vectice import Resource, DatasetSourceOrigin, FilesMetadata

        class MyResource(Resource):
            _origin = "Data source name"

            def __init__(
                self,
                paths: str | list[str],
            ):
                super().__init__(paths=paths)

            def _build_metadata(self) -> FilesMetadata:  # (1)
                files = ...  # fetch file list from your custom storage
                total_size = ...  # compute total file size, retrieve them from self._paths
                return FilesMetadata(
                    size=total_size,
                    origin=self._origin,
                    files=files,
                    usage=self.usage,
                )

            def _fetch_data(self) -> dict[str, bytes]:
                files_data = {}
                for file in self.metadata.files:
                    file_contents = ...  # fetch file contents from your custom storage
                    files_data[file.name] = file_contents
                return files_data
        ```

        1. Return [FilesMetadata][vectice.models.resource.metadata.FilesMetadata] for data stored in files,
            [DBMetadata][vectice.models.resource.metadata.DBMetadata] for data stored in a database.
    """

    # origin must be a string because users can subclass resources
    # and set a custom origin
    _origin: str = DatasetSourceOrigin.OTHER.value

    _files_limit = 5000

    @abstractmethod
    def __init__(
        self,
        paths: list[str] | str,
        dataframes: TDataFrameType | list[TDataFrameType] | None = None,
        capture_schema_only: bool = False,
        columns_description: dict[str, str] | str | None = None,
    ):
        """Initialize a resource."""
        self._metadata: Metadata | None = None
        self._data: dict | None = None
        if paths:
            self._paths = paths if isinstance(paths, list) else [paths]
        else:
            self._paths = paths
        self.capture_schema_only = capture_schema_only

        self._dataframes = dataframes if isinstance(dataframes, list) or dataframes is None else [dataframes]
        if self._dataframes is not None:
            for dataframe in self._dataframes:
                if dataframe is not None and not isinstance(  # pyright: ignore[reportUnnecessaryComparison]
                    dataframe, get_args(DataFrameType)
                ):
                    raise ValueError(
                        f"Argument 'dataframe' of type '{type(dataframe)}' is invalid, only Pandas, Spark and H2O DataFrame are supported."
                    )

        self.columns_description = columns_description

    @property
    def data(self) -> dict:
        """The resource's data.

        Returns:
            The resource's data.
        """
        if self._data is None:
            self._data = self._fetch_data()
        return self._data

    @abstractmethod
    def _fetch_data(
        self,
    ) -> dict:
        pass

    @abstractmethod
    def _build_metadata(self) -> Metadata:
        pass

    @property
    def metadata(self) -> Metadata:
        """The resource's metadata.

        Returns:
            The resource's metadata.
        """
        if self._metadata is None:
            self._metadata = self._build_metadata()
        return self._metadata

    @metadata.setter
    def metadata(self, value: Metadata):
        """Set the resource's metadata.

        Parameters:
            value: The metadata to set.
        """
        self._metadata = value

    @property
    def usage(self) -> DatasetSourceUsage | None:
        """The resource's usage.

        Returns:
            The resource's usage.
        """
        return self.metadata.usage

    @usage.setter
    def usage(self, value: DatasetSourceUsage):
        """Set the resource's usage.

        Parameters:
            value: The usage to set.
        """
        self.metadata.usage = value
