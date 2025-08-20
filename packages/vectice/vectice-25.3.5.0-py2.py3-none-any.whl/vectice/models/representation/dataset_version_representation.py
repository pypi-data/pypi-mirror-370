from __future__ import annotations

import logging
import os
from functools import reduce
from typing import TYPE_CHECKING, Any, Dict

from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.models.attachment import TAttachment
from vectice.models.attachment_container import AttachmentContainer
from vectice.models.property import Property
from vectice.models.representation.attachment import Attachment
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.resource_item_representation import ResourceItemRepresentation
from vectice.utils.common_utils import (
    flatten_resources,
    format_attachments,
    format_properties,
    repr_class,
    strip_dict_list,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe
from vectice.utils.filesize import size

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.api.client import Client
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation


_logger = logging.getLogger(__name__)


class DatasetVersionRepresentation:
    """Represents the metadata of a Vectice dataset version.

    A Dataset Version Representation shows information about a specific version of a dataset from the Vectice app. It makes it easier to get and read this information through the API.

    NOTE: **Hint**
        A dataset version ID starts with 'DTV-XXX'. Retrieve the ID in the Vectice App, then use the ID with the following methods to get the dataset version:
        ```connect.dataset_version('DTV-XXX')``` or ```connect.browse('DTV-XXX')```
        (see [Connection page](https://api-docs.vectice.com/reference/vectice/connection/#vectice.Connection.dataset_version)).

    Attributes:
        id (str): The unique identifier of the dataset version.
        project_id (str): The identifier of the project to which the dataset version belongs.
        name (str): The name of the dataset version. For dataset versions it corresponds to the version number.
        description (str): The description of the dataset version.
        properties (List[Dict[str, Any]]): The properties associated with the dataset version.
        resources (List[Dict[str, Any]]): The resources summary with the type, number of files and aggregated total number of columns for each resource inside the dataset version.
        iteration_origin (str | None): The iteration in which this dataset version was created.
        phase_origin (str | None): The phase in which this dataset version was created.
        dataset_representation (DatasetRepresentation): Holds informations about the source dataset linked to the dataset version, where all versions are grouped together.
        creator (Dict[str, str]): Creator of the dataset version.
    """

    def __init__(
        self, output: DatasetVersionRepresentationOutput, client: Client, dataset: DatasetRepresentation | None = None
    ):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.is_starred = output.is_starred
        self.description = output.description
        self.properties = strip_dict_list(output.properties)
        self.resources = output.resources
        self.iteration_origin = output.iteration_origin
        self.phase_origin = output.phase_origin
        self.dataset_representation = dataset if dataset else DatasetRepresentation(output.dataset, client)
        self.creator = output.creator
        self._client = client
        self._output = output

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the DatasetVersionRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        flat_properties = {prop["key"]: prop["value"] for prop in self.properties}
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "is_starred": self.is_starred,
            "description": self.description,
            "properties": flat_properties,
            "resources": flatten_resources(self.resources),
            "iteration_origin": self.iteration_origin,
            "phase_origin": self.phase_origin,
            "dataset_representation": (
                self.dataset_representation._asdict()  # pyright: ignore reportPrivateUsage
                if self.dataset_representation
                else None
            ),
            "creator": self.creator,
        }

    def properties_as_dataframe(self) -> DataFrame:
        """Transforms the properties of the DatasetVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the properties of the dataset version.
        """
        return repr_list_as_pd_dataframe(self.properties)

    def resources_as_dataframe(self) -> DataFrame:
        """Transforms the resources of the DatasetVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the resources of the dataset version.
        """
        return repr_list_as_pd_dataframe(
            reduce(
                lambda acc, res: [*acc, {**res, "size": size(int(res["size"])) if res["size"] is not None else None}],
                self.resources,
                [],
            )
        )

    def list_resources_items(self) -> list[ResourceItemRepresentation]:
        """Lists all the resources items of the DatasetVersionRepresentation.

        Returns:
            The list of the resources items.
        """
        return [
            ResourceItemRepresentation(output, self._client)
            for output in self._client.list_resources_items(self.id, None)
        ]

    def update(
        self,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: TAttachment | None = None,
        columns_description: dict[str, str] | str | None = None,
    ) -> None:
        """Update the Dataset Version from the API.

        Parameters:
            properties: The new properties of the dataset.
            attachments: The new attachments of the dataset.
            columns_description: A dictionary or path to a csv file to map the column's name to a specific description. Should follow the format { "column_name": "Description", ... }

        Returns:
            None
        """
        if properties is not None:
            self._upsert_properties(properties)

        if attachments is not None:
            self._update_attachments(attachments)

        if columns_description is not None:
            self._update_dataset_version(columns_description)

    def _upsert_properties(self, properties: dict[str, str | int] | list[Property] | Property):
        clean_properties = list(map(lambda property: property.key_val_dict(), format_properties(properties)))
        new_properties = self._client.upsert_properties("dataSetVersion", self.id, clean_properties)
        self.properties = strip_dict_list(new_properties)
        _logger.info(f"Dataset version {self.id!r} properties successfully updated.")

    def _update_attachments(self, attachments: TAttachment):
        container = AttachmentContainer(self._output, self._client)
        container.upsert_attachments(format_attachments(attachments))
        _logger.info(f"Dataset version {self.id!r} attachments successfully updated.")

    def _update_dataset_version(self, columns_description: dict[str, str] | str):
        if isinstance(columns_description, str):
            self._client.update_columns_description_via_csv(self.id, columns_description)
        else:
            items = columns_description.items()
            list_columns_description = list(map(lambda x: {"name": x[0], "description": x[1]}, items))
            self._client.update_dataset_version(self.id, list_columns_description)

        self._client.warn_if_dataset_version_columns_are_missing_description(self.id)
        _logger.info(f"Dataset version {self.id!r} columns descriptions successfully updated.")

    def list_attachments(self) -> list[Attachment]:
        """Retrieves a list of attachments and prints the attachments in a table format associated with the current dataset version.

        Returns:
            list[Attachment]: A list of `Attachment` instances corresponding
            to the dataset version.
        """
        return self._client.list_attachments(self)

    def download_attachments(self, attachments: list[str] | str | None = None, output_dir: str | None = None) -> None:
        """Downloads a list of attachments associated with the current dataset version.

        Parameters:
            attachments: A list of attachment file names or a single attachment file name
                                                  to be downloaded. If None, all attachments will be downloaded.
            output_dir: The directory path where the attachments will be saved.
                                      If None, the current working directory is used.

        Returns:
            None
        """
        if output_dir is None:
            output_dir = os.getcwd()
        os.makedirs(output_dir, exist_ok=True)

        if attachments is None:
            attachments = list(map(lambda attach: attach.name, self.list_attachments()))

        if isinstance(attachments, str):
            attachments = [attachments]

        for attachment in attachments:
            self._client.download_attachment(self, attachment, output_dir)

    def get_table(self, table: str) -> DataFrame:
        """Retrieves a table associated with the current dataset version.

        Parameters:
            table: The name of the table.

        Returns:
            The data from the specified table as a DataFrame.
        """
        return repr_list_as_pd_dataframe(self._client.get_version_table(self, table))

    def list_lineage_inputs(self) -> list[DatasetVersionRepresentation]:
        """Retrieves all the lineage inputs of the current dataset version.

        Returns:
            The list of dataset version used as input of the current dataset version.
        """
        return list(
            map(
                lambda output: DatasetVersionRepresentation(output, self._client),
                self._client.get_lineage_inputs(self.id, "dtv"),
            )
        )

    def list_lineage_children(self) -> list[DatasetVersionRepresentation | ModelVersionRepresentation]:
        """Retrieves all the lineage children of the current dataset version.

        Returns:
            The list of dataset version or model version where the current dataset version is used as input.
        """
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        mdvs, dtvs = self._client.get_lineage_children(self.id, "dtv")
        return [
            *list(map(lambda output: ModelVersionRepresentation(output, self._client), mdvs)),
            *list(map(lambda output: DatasetVersionRepresentation(output, self._client), dtvs)),
        ]

    def has_column(self, column: str) -> bool:
        """Identifies if this dataset version has a column with name matching the column parameter.

        Parameters:
            column: The name of column to search for.

        Returns:
            Whether the dataset version has a column matching that name or not.
        """
        return self._client.has_column(self.id, column)
