from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List

from vectice.api.json.model_representation import ModelRepresentationOutput
from vectice.utils.api_utils import DEFAULT_MAX_SIZE, DEFAULT_NUMBER_OF_ITEMS
from vectice.utils.common_utils import (
    convert_keys_to_snake_case,
    flatten_dict,
    process_versions_list_metrics_and_properties,
    process_versions_origins,
    remove_type_name,
    repr_class,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.api.client import Client
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

_logger = logging.getLogger(__name__)


class ModelRepresentation:
    """Represents the metadata of a Vectice model.

    A Model Representation shows information about a specific model from the Vectice app. It makes it easier to get and read this information through the API.
    This includes high level information about the various versions of the model.

    NOTE: **Hint**
        A model ID starts with 'MDL-XXX'. Retrieve the ID in the Vectice App, then use the ID with the following methods to get the model:
        ```connect.model('MDL-XXX')``` or ```connect.browse('MDL-XXX')```
        (see [Connection page](https://api-docs.vectice.com/reference/vectice/connection/#vectice.Connection.model)).

    Attributes:
        id (str): The unique identifier of the model.
        project_id (str): The identifier of the project to which the model belongs.
        name (str): The name of the model.
        description (str): The description of the model.
        type (str): The type of the model
        total_number_of_versions (int): The total number of versions belonging to this model.
        versions_status (Dict[str, Any]): Aggregated information about the statuses of model versions within the model (e.g., number of versions in production, staging...).
    """

    def __init__(
        self,
        output: ModelRepresentationOutput,
        client: "Client",
    ):
        self.id = output.id
        self.name = output.name
        self.type = output.type
        self.description = output.description
        self.version_status = output.version_stats
        self.total_number_of_versions = output.total_number_of_versions
        self.project_id = output.project_id

        self._last_version = output.version
        self._client = client

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the ModelRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "description": self.description,
            "type": self.type,
            "version_status": self.version_status,
            "total_number_of_versions": self.total_number_of_versions,
        }

    def list_versions(
        self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS, as_dataframe: bool = False
    ) -> List[ModelVersionRepresentation] | DataFrame:
        """Retrieve the model versions list linked to the model. (Maximum of 100 versions).

        Parameters:
            number_of_items: The number of versions to retrieve. Defaults to 30.
            as_dataframe: If set to True, return type will be a pandas DataFrame for easier manipulation (requires pandas to be installed).
                                 If set to False, returns all model versions as a list of ModelVersionRepresentation.

        Returns:
            The model versions list as either a list of ModelVersionRepresentation or a pandas DataFrame.
        """
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 versions will be retrieved. For additional versions, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE

        version_list = self._client.get_model_version_list(self.id, number_of_items).list
        model_version_list = [ModelVersionRepresentation(version, self._client, self) for version in version_list]

        if not as_dataframe:
            return model_version_list

        convert_origins = process_versions_origins(version_list)
        clean_version_list = remove_type_name(convert_origins)
        converted_version_list = [
            convert_keys_to_snake_case(versions)  # pyright: ignore[reportArgumentType]
            for versions in clean_version_list
        ]
        processed_version_list = process_versions_list_metrics_and_properties(converted_version_list)

        for versions in processed_version_list:
            versions.update(flatten_dict(versions))
            versions["all_properties_dict"] = versions["properties"]
            versions["all_metrics_dict"] = versions["metrics"]
            del versions["properties"]
            del versions["metrics"]
        try:
            return repr_list_as_pd_dataframe(processed_version_list)
        except ModuleNotFoundError:
            _logger.info(
                "To display the list of versions as a DataFrame, pandas must be installed. Your list of versions will be in the format of a list of dictionaries."
            )
            return model_version_list
