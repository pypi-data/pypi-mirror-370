from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List

from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.utils.api_utils import DEFAULT_MAX_SIZE, DEFAULT_NUMBER_OF_ITEMS
from vectice.utils.common_utils import (
    convert_keys_to_snake_case,
    flatten_dict,
    flatten_resources,
    process_versions_list_metrics_and_properties,
    process_versions_origins,
    remove_type_name,
    repr_class,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.api.client import Client
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation

_logger = logging.getLogger(__name__)


class DatasetRepresentation:
    """Represents the metadata of a Vectice dataset.

    A Dataset Representation shows information about a specific dataset from the Vectice app. It makes it easier to get and read this information through the API.

    NOTE: **Hint**
        A dataset ID starts with 'DTS-XXX'. Retrieve the ID in the Vectice App, then use the ID with the following methods to get the dataset:
        ```connect.dataset('DTS-XXX')``` or ```connect.browse('DTS-XXX')```
        (see [Connection page](https://api-docs.vectice.com/reference/vectice/connection/#vectice.Connection.dataset)).

    Attributes:
        id (str): The unique identifier of the dataset.
        project_id (str): The identifier of the project to which the dataset belongs.
        name (str): The name of the dataset.
        description (str): The description of the dataset.
        type (str): The type of the dataset.
        origin (str): The source origin of the dataset.
        total_number_of_versions (int): The total number of versions belonging to this dataset.
    """

    def __init__(
        self,
        output: DatasetRepresentationOutput,
        client: "Client",
    ):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.type = output.type
        self.origin = output.origin
        self.description = output.description
        self.total_number_of_versions = output.total_number_of_versions
        self._last_version = output.version
        self._client = client

    def __repr__(self):
        return repr_class(self)

    def _asdict(self):
        return self.asdict()

    def asdict(self) -> Dict[str, Any]:
        """Transform the DatasetRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "description": self.description,
            "type": self.type,
            "origin": self.origin,
            "total_number_of_versions": self.total_number_of_versions,
        }

    def list_versions(
        self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS, as_dataframe: bool = False
    ) -> List[DatasetVersionRepresentation] | DataFrame:
        """Retrieve the dataset versions list linked to the dataset. (Maximum of 100 versions).

        Parameters:
            number_of_items: The number of versions to retrieve. Defaults to 30.
            as_dataframe: If set to True, return type will be a pandas DataFrame for easier manipulation (requires pandas to be installed).
                            If set to False, returns all dataset versions as a list of DatasetVersionRepresentation.

        Returns:
            The dataset versions list as either a list of DatasetVersionRepresentation or a pandas DataFrame.
        """
        from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation

        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 versions will be retrieved. For additional versions, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE

        version_list = self._client.get_dataset_version_list(self.id, number_of_items).list

        if not as_dataframe:
            return [DatasetVersionRepresentation(version, self._client, self) for version in version_list]

        for version in version_list:
            version["datasetSources"] = flatten_resources(version.resources)
        convert_origins = process_versions_origins(version_list)
        clean_version_list = remove_type_name(convert_origins)
        converted_version_list = [
            convert_keys_to_snake_case(versions)  # pyright: ignore[reportArgumentType]
            for versions in clean_version_list
        ]
        processed_version_list = process_versions_list_metrics_and_properties(converted_version_list)
        for versions in processed_version_list:
            versions.update(flatten_dict(versions))
            del versions["dataset_sources"]
            versions["all_properties_dict"] = versions["properties"]
            del versions["properties"]
        try:
            return repr_list_as_pd_dataframe(processed_version_list)
        except ModuleNotFoundError:
            _logger.info(
                "To display the list of versions as a DataFrame, pandas must be installed. Your list of versions will be in the format of a list of dictionaries."
            )
            return [DatasetVersionRepresentation(version, self._client, self) for version in version_list]
