from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from vectice.api.json.dataset_resource_representation import DatasetResourceRepresentationOutput
from vectice.utils.common_utils import repr_class

if TYPE_CHECKING:
    from vectice.api.client import Client


class ResourceItemRepresentation:
    """Represents the metadata of a Vectice resource.

    An Resource Item Representation shows information about a specific resource item from the Vectice app.
    It makes it easier to get and read this information through the API.

    Attributes:
        path (str): The path of the resource.
        name (str): The name of the resource.
        usage (str): The usage of the resource.
        size (int | None): The size of the resource.
        columns_number (int | None): The columns number of the resource.
        rows_number (int | None): The number of rows of the resource.
        info (dict | None): The extra information of the resource.
    """

    def __init__(self, output: DatasetResourceRepresentationOutput, client: Client):
        self.name = output.name
        self.resource_type = output.usage
        self.path = output.path
        self.size = output.size
        self.columns_number = output.columns_count
        self.rows_number = output.rows_count
        self.info = output.info
        self._type = output.type
        self._client = client
        self._id = output.id

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the ResourceItemRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        return {
            "name": self.name,
            "resource_type": self.resource_type,
            "path": self.path,
            "size": self.size,
            "columns_number": self.columns_number,
            "rows_number": self.rows_number,
            "info": self.info,
        }

    def list_columns(self) -> list[Dict[str, Any]]:
        """Lists all the columns of the item.

        Returns:
            The columns list.
        """
        return self._client.list_columns(self._id, self._type)
