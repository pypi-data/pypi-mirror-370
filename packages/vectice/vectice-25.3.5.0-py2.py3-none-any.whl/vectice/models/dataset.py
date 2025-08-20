from __future__ import annotations

import csv
import functools
import logging
from datetime import datetime
from typing import Union

from typing_extensions import get_args

from vectice.api.http_error_handlers import VecticeException
from vectice.models.attachment import TAttachment, TFormattedAttachment
from vectice.models.property import Property
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.resource.base import Resource
from vectice.models.resource.metadata.base import DatasetSourceType, DatasetSourceUsage, DatasetType, MetadataSettings
from vectice.models.resource.snowflake_resource import SnowflakeResource
from vectice.models.resource.spark_table_resource import SparkTableResource
from vectice.utils.common_utils import format_attachments, format_properties

_logger = logging.getLogger(__name__)

TBaseDerivedFrom = Union[str, DatasetRepresentation, DatasetVersionRepresentation]


class Dataset:
    def __init__(
        self,
        type: DatasetType,
        name: str | None = None,
        resource: Resource | None = None,
        training_resource: Resource | None = None,
        testing_resource: Resource | None = None,
        validation_resource: Resource | None = None,
        derived_from: list[TBaseDerivedFrom | Dataset] | TBaseDerivedFrom | Dataset | None = None,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: TAttachment | None = None,
    ):
        self._type = type
        self._name = name or f"dataset {datetime.now()}"
        self._resource = resource
        self._training_resource = training_resource
        self._testing_resource = testing_resource
        self._validation_resource = validation_resource
        self._derived_from = get_derived_from(derived_from)
        self._latest_version_id: str | None = None
        self._properties = format_properties(properties) if properties else None
        self._attachments = format_attachments(attachments) if attachments else None

        if self._type is DatasetType.MODELING:
            if self._training_resource is None or self._testing_resource is None:
                raise ValueError("You cannot create a modeling dataset without both training and testing sets")

            self._training_resource.usage = DatasetSourceUsage.TRAINING
            self._testing_resource.usage = DatasetSourceUsage.TESTING
            if self._validation_resource:
                self._validation_resource.usage = DatasetSourceUsage.VALIDATION

        self._has_snowflake_resource = (
            isinstance(self._resource, SnowflakeResource)
            or isinstance(self._training_resource, SnowflakeResource)
            or isinstance(self._testing_resource, SnowflakeResource)
            or isinstance(self._validation_resource, SnowflakeResource)
        )
        self._has_spark_resource = (
            isinstance(self._resource, SparkTableResource)
            or isinstance(self._training_resource, SparkTableResource)
            or isinstance(self._testing_resource, SparkTableResource)
            or isinstance(self._validation_resource, SparkTableResource)
        )

        metadata_dict, is_updating_columns = self._transform_resource_to_metadata_dict()
        self._is_updating_columns = is_updating_columns
        self._metadata_as_dict = metadata_dict

    @staticmethod
    def origin(
        resource: Resource,
        name: str | None = None,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: str | list[str] | None = None,
    ) -> Dataset:
        """Create an origin dataset.

        Examples:
            ```python
            from vectice import Dataset, FileResource

            dataset = Dataset.origin(
                name="my origin dataset",
                resource=FileResource(paths="origin_dataset.csv"),
            )
            ```

        Parameters:
            resource: The resource for the origin dataset.
            name: The name of the dataset.
            properties: A dict, for example `{"folds": 32}`.
            attachments: The file paths that will be attached to the iteration along with the dataset.
        """
        return Dataset(
            type=DatasetType.ORIGIN,
            name=name,
            resource=resource,
            properties=properties,
            attachments=attachments,
        )

    @staticmethod
    def clean(
        resource: Resource,
        name: str | None = None,
        derived_from: list[TBaseDerivedFrom | Dataset] | TBaseDerivedFrom | Dataset | None = None,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: str | list[str] | None = None,
    ) -> Dataset:
        """Create a clean dataset.

        Examples:
            ```python
            from vectice import Dataset, FileResource

            dataset = Dataset.clean(
                name="my clean dataset",
                resource=FileResource(paths="clean_dataset.csv"),
            )
            ```

        Parameters:
            resource: The resource for the clean dataset.
            name: The name of the dataset.
            derived_from: List of dataset versions or model versions (or their ids) from which this dataset is derived.
            properties: A dict, for example `{"folds": 32}`.
            attachments: The file paths that will be attached to the iteration along with the dataset.
        """
        return Dataset(
            type=DatasetType.CLEAN,
            name=name,
            resource=resource,
            derived_from=derived_from,
            properties=properties,
            attachments=attachments,
        )

    @staticmethod
    def modeling(
        training_resource: Resource,
        testing_resource: Resource,
        validation_resource: Resource | None = None,
        name: str | None = None,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: str | list[str] | None = None,
        derived_from: list[TBaseDerivedFrom | Dataset] | TBaseDerivedFrom | Dataset | None = None,
    ) -> Dataset:
        """Create a modeling dataset.

        Examples:
            ```python
            from vectice import Dataset, FileResource

            dataset = Dataset.modeling(
                name="my modeling dataset",
                training_resource=FileResource(paths="training_dataset.csv"),
                testing_resource=FileResource(paths="testing_dataset.csv"),
                validation_resource=FileResource(paths="validation_dataset.csv"),
            )
            ```

        Parameters:
            training_resource: The resource for the training set (for modeling datasets).
            testing_resource: The resource for the testing set (for modeling datasets).
            validation_resource: The resource for the validation set (optional, for modeling datasets).
            name: The name of the dataset.
            properties: A dict, for example `{"folds": 32}`.
            attachments: The file paths that will be attached to the iteration along with the dataset.
            derived_from: List of dataset versions or model versions (or their ids) from which this dataset is derived.
        """
        return Dataset(
            type=DatasetType.MODELING,
            name=name,
            training_resource=training_resource,
            testing_resource=testing_resource,
            validation_resource=validation_resource,
            properties=properties,
            attachments=attachments,
            derived_from=derived_from,
        )

    def __repr__(self):
        return f"Dataset(name={self.name!r}, type={self.type!r})"

    @property
    def type(self) -> DatasetType:
        """The dataset's type.

        Returns:
            The dataset's type.
        """
        return self._type

    @property
    def resource(self) -> Resource | tuple[Resource, Resource, Resource | None]:
        """The dataset's resource.

        Returns:
            The dataset's resource.
        """
        if self._type is DatasetType.MODELING:
            return self._training_resource, self._testing_resource, self._validation_resource  # type: ignore[return-value]
        return self._resource  # type: ignore[return-value]

    @property
    def name(self) -> str:
        """The dataset's name.

        Returns:
            The dataset's name.
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Set the dataset's name.

        Parameters:
            name: The name of the dataset.
        """
        self._name = name

    @property
    def derived_from(self) -> list[str]:
        """The datasets versions or models versions from which this dataset is derived.

        Returns:
            The datasets versions or models versions from which this dataset is derived.
        """
        return self._derived_from

    @property
    def latest_version_id(self) -> str | None:
        """The id of the latest version of this dataset.

        Returns:
            The id of the latest version of this dataset.
        """
        return self._latest_version_id

    @latest_version_id.setter
    def latest_version_id(self, value: str) -> None:
        """Set the id of the latest version of this dataset.

        Parameters:
            value: The id of the latest version of this dataset.
        """
        self._latest_version_id = value

    @property
    def properties(self) -> list[Property] | None:
        """The dataset's properties.

        Returns:
            The dataset's properties.
        """
        return self._properties

    @properties.setter
    def properties(self, properties: dict[str, str | int] | list[Property] | Property | None):
        """Set the dataset's properties.

        Parameters:
            properties: The properties of the dataset.
        """
        _logger.warning("To save your updated dataset properties, you must reassign your dataset to an iteration.")
        self._properties = format_properties(properties) if properties else None

    @property
    def attachments(self) -> list[TFormattedAttachment] | None:
        """The file attachment objects or paths associated with the dataset.

        Returns:
        `List[Union[Table, str]] | None`
            A list of attachment objects, where each attachment is one of:

        - `Table`
            A formatted table object containing structured data
        - `str`
            A string representation of an attachment (e.g., file path)
        - `None`
            If no attachments are present
        """
        return self._attachments

    @attachments.setter
    def attachments(self, attachments: TAttachment):
        """Attach a file or files to the dataset.

        Parameters:
            attachments: The filename or filenames of the file or set of files to attach to the dataset.
        """
        self._attachments = format_attachments(attachments)

    def _transform_resource_to_metadata_dict(self):
        from vectice.api.client import Client

        resources = self.resource if isinstance(self.resource, tuple) else [self.resource]
        metadata_asdict = []
        is_updating_columns = False

        org_config = Client.get_instance().org_config
        settings = MetadataSettings(
            minimum_rows_for_statistics=org_config.configuration.df_statistics_row_threshold,
            sample_rows_for_statistics=org_config.configuration.df_statistics_row_sample,
            maximum_columns_for_statistics=org_config.configuration.df_statistics_colmns_threshold,
        )

        for resource in resources:
            if resource is not None and resource.metadata:
                resource.metadata.set_settings(settings)

                metadata, columns_description = resource.metadata, resource.columns_description
                is_updating_columns = is_updating_columns is False and columns_description is not None
                columns = columns_description or {}
                metadata_dict, type = metadata.asdict(), metadata.type
                if type == DatasetSourceType.DB:
                    for db in metadata_dict["dbs"]:
                        db["columns"] = self._combine_source_column_description(db, columns)
                else:
                    for file in metadata_dict["files"]:
                        file["columns"] = self._combine_source_column_description(file, columns)

                metadata_asdict.append(metadata_dict)
        return metadata_asdict, is_updating_columns

    def _combine_source_column_description(self, source: dict, columns_description: dict[str, str] | str):
        def _transform_path_to_dictionary(path: str):
            def _reduce_csv(acc: dict[str, str], curr: list[str]):
                if len(curr) > 1:
                    return {**acc, curr[0]: curr[1]}
                return acc

            with open(path, mode="r", newline="") as csv_file:
                return functools.reduce(_reduce_csv, csv.reader(csv_file), {})

        if isinstance(columns_description, str):
            columns_description = _transform_path_to_dictionary(columns_description)

        def _map_columns(col: dict):
            col_name = col["name"]
            if col_name in columns_description:
                column_desc = columns_description[col_name]
                return {**col, "description": column_desc}
            return col

        return list(map(_map_columns, source["columns"]))


TDerivedFrom = Union[TBaseDerivedFrom, Dataset]


def get_derived_from(
    derived_from: list[TDerivedFrom] | TDerivedFrom | None,
) -> list[str]:

    from vectice.models.model import Model
    from vectice.models.representation.model_representation import ModelRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    derived_from_ids: list[str] = []
    formatted_df = _format_derived_from(derived_from)
    for df in formatted_df or []:
        if isinstance(df, Dataset):
            if df.latest_version_id is None:
                raise ValueError(
                    f"Dataset {df.name!r} does not have a version id. "
                    "Was it registered in Vectice (logged to an iteration)?"
                )
            derived_from_ids.append(df.latest_version_id)
        elif isinstance(df, Model):
            if df.latest_version_id is None:
                raise ValueError(
                    f"Model {df.name!r} does not have a version id. "
                    "Was it registered in Vectice (logged to an iteration)?"
                )
            derived_from_ids.append(df.latest_version_id)
        elif isinstance(df, DatasetRepresentation) or isinstance(df, ModelRepresentation):
            last_version = df._last_version  # pyright: ignore[reportPrivateUsage]
            if last_version is None:
                raise VecticeException("Unable to log asset, no versions exist.")
            derived_from_ids.append(last_version.id)
        elif isinstance(df, DatasetVersionRepresentation) or isinstance(df, ModelVersionRepresentation):
            derived_from_ids.append(df.id)
        elif isinstance(df, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            if df.startswith("DTV-") or df.startswith("MDV-"):
                derived_from_ids.append(df)
            else:
                raise VecticeException(f"Please check the derived_from id {df}.")
    return derived_from_ids


def _format_derived_from(derived_from: list[TDerivedFrom] | TDerivedFrom | None) -> list[TDerivedFrom]:
    if derived_from is None:
        return []

    formatted_derived_from = derived_from if isinstance(derived_from, list) else [derived_from]

    for df in formatted_derived_from:
        if not isinstance(df, get_args(TDerivedFrom)):
            raise ValueError("Invalid derived_from parameter")

    return formatted_derived_from
