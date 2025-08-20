from __future__ import annotations

import logging
from functools import reduce
from typing import TYPE_CHECKING, Any, Dict

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.api.json.dataset_resource_representation import DatasetResourceRepresentationOutput
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.paged_response import PagedResponse
from vectice.models.resource.metadata.base import DatasetSourceType, DatasetSourceUsage
from vectice.utils.api_utils import DEFAULT_NUMBER_OF_ITEMS, PAGINATE_OUTPUT, get_page_input

if TYPE_CHECKING:
    from vectice.api.json.dataset_register import DatasetRegisterInput, DatasetRegisterOutput
    from vectice.api.json.iteration import IterationContextInput


_logger = logging.getLogger(__name__)

# TODO JobRun for lineages
_RETURNS = """
            datasetVersion {
                          vecticeId
                          name
                          origin {
                            id
                          }
                          dataSet {
                            name
                            projectId
                          }


            }
            useExistingDataset
            useExistingVersion
            __typename
            """

_RETURNS_DATASET = """
            vecticeId
            createdDate
            updatedDate
            name
            description
            type
            sourceOrigin
            versionCount
            lastVersion {
                vecticeId
                createdDate
                updatedDate
                name
                description
                __typename
            }
            project {
                vecticeId
            }
            __typename
"""

_BASE_DATASET_VERSION = """
            vecticeId
            createdDate
            updatedDate
            isStarred
            name
            description
            sourceOrigin
            createdBy {
                name
                email
            }
            properties {
                key
                value
            }
            __typename
"""

_LIST_VERSION = f"""
            {_BASE_DATASET_VERSION}
            origins {{
                phase {{
                    vecticeId
                    __typename
                }}
                iteration {{
                    vecticeId
                    __typename
                }}
                __typename
            }}
            datasetSources {{
                size
                usage
                itemsCount
                columnsCount
            }}
"""

RETURNS_DATASET_VERSION = f"""
            {_BASE_DATASET_VERSION}
            origins {{
                phase {{
                    vecticeId
                    __typename
                }}
                iteration {{
                    vecticeId
                    __typename
                }}
                __typename
            }}
            dataSet {{
                vecticeId
                name
                project {{
                    vecticeId
                }}
                sourceOrigin
                type
                description
                versionCount
                lastVersion {{
                    vecticeId
                    __typename
                }}
            }}
            datasetSources {{
                usage
                itemsCount
                size
                columnsCount
            }}
"""


_RETURNS_EMPTY_DATASET_VERSION = """
            vecticeId
            __typename
"""


_RETURNS_DATASET_SOURCES = """
        id
        type
        usage
        files {
            items {
                id
                name
                filename
                size
                rowsNumber
                columnsNumber
                uri
                extraMetadata {
                    key
                    value
                    displayName
                }
                __typename
            }
        }
        tables {
            items {
                id
                name
                tablename
                size
                rowsNumber
                columnsNumber
                uri
                extraMetadata {
                    key
                    value
                    displayName
                }
                __typename
            }
        }
        __typename
"""

_RETURNS_COLUMNS = PAGINATE_OUTPUT.format(
    """
    name
    categoryType
    description
    statistics {
        numerical {
            mean
            stdDeviation
            quantiles {
                qMin
                q25
                q50
                q75
                qMax
            }
            missing
        }
        text {
            unique
            missing
            mostCommons {
                value
                frequency
            }
        }
        date {
            minimum
            maximum
            median
            mean
            missing
        }
        boolean {
            true
            false
            missing
        }
    }
"""
)

_RETURNS_PAGINATED_DATASET_LIST = PAGINATE_OUTPUT.format(_RETURNS_DATASET)
_RETURNS_PAGINATED_VERSION_LIST = PAGINATE_OUTPUT.format(_LIST_VERSION)


class GqlDatasetApi(GqlApi):
    def get_dataset(self, id: str) -> DatasetRepresentationOutput:
        variable_types = "$datasetId:VecticeId!"
        kw = "datasetId:$datasetId"
        variables = {"datasetId": id}
        query = GqlApi.build_query(
            gql_query="getDataset",
            variable_types=variable_types,
            returns=_RETURNS_DATASET,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: DatasetRepresentationOutput = Parser().parse_item(response["getDataset"])
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset", id)

    def get_dataset_list(
        self, project_id: str, size: int = DEFAULT_NUMBER_OF_ITEMS
    ) -> PagedResponse[DatasetRepresentationOutput]:
        variable_types = "$projectId:VecticeId!,$page:PageInput"
        kw = "projectId:$projectId,page:$page"
        variables = {
            "projectId": project_id,
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query="getDatasetList",
            variable_types=variable_types,
            returns=_RETURNS_PAGINATED_DATASET_LIST,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: PagedResponse[DatasetRepresentationOutput] = Parser().parse_paged_response(
                response["getDatasetList"]
            )
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "project", project_id)

    def get_dataset_version_list(
        self, id: str, size: int = DEFAULT_NUMBER_OF_ITEMS
    ) -> PagedResponse[DatasetVersionRepresentationOutput]:
        gql_query = "getDatasetVersionsList"
        variable_types = "$datasetId:VecticeId!,$page:PageInput"
        kw = "datasetId:$datasetId,page:$page"
        variables = {
            "datasetId": id,
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_PAGINATED_VERSION_LIST,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: PagedResponse[DatasetVersionRepresentationOutput] = Parser().parse_paged_response(
                response[gql_query]
            )
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_version", id)

    def get_dataset_version(self, id: str) -> DatasetVersionRepresentationOutput:
        variable_types = "$datasetVersionId:VecticeId!"
        kw = "datasetVersionId:$datasetVersionId"
        variables = {"datasetVersionId": id}
        query = GqlApi.build_query(
            gql_query="getDatasetVersion",
            variable_types=variable_types,
            returns=RETURNS_DATASET_VERSION,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: DatasetVersionRepresentationOutput = Parser().parse_item(response["getDatasetVersion"])
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_version", id)

    def get_dataset_version_has_columns_without_description(self, id: str) -> bool:
        variable_types = "$datasetVersionId:VecticeId!"
        kw = "datasetVersionId:$datasetVersionId"
        variables = {"datasetVersionId": id}
        query = GqlApi.build_query(
            gql_query="getDatasetVersion",
            variable_types=variable_types,
            returns="hasColumnWithoutDescription",
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            return self.execute(query_built, variables)["getDatasetVersion"]["hasColumnWithoutDescription"]
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_version", id)

    def register_dataset(
        self,
        data: DatasetRegisterInput,
        iteration_context: IterationContextInput,
    ) -> DatasetRegisterOutput:
        variables: dict[str, Any] = {"iterationContext": iteration_context, "data": data}
        kw = "iterationContext:$iterationContext,data:$data"
        variable_types = "$iterationContext:IterationContextInput!,$data:DatasetRegisterInput!"

        query = GqlApi.build_query(
            gql_query="registerDataset",
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: DatasetRegisterOutput = Parser().parse_item(response["registerDataset"])
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset", "register dataset")

    def update_dataset_version(self, id: str, columns_description: list[dict[str, str]]):
        variable_types = "$datasetVersionId:VecticeId!,$data:DatasetVersionUpdateInput!"
        kw = "datasetVersionId:$datasetVersionId,data:$data"
        variables = {"datasetVersionId": id, "data": {"columnsDescription": columns_description}}
        query = GqlApi.build_query(
            gql_query="updateDatasetVersion",
            variable_types=variable_types,
            returns=_RETURNS_EMPTY_DATASET_VERSION,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_version", id)

    def has_column(self, id: str, column: str) -> bool:
        variable_types = "$datasetVersionId:VecticeId!,$column:String!"
        kw = "datasetVersionId:$datasetVersionId,column:$column"
        variables = {"datasetVersionId": id, "column": column}
        query = GqlApi.build_query(
            gql_query="hasColumn",
            variable_types=variable_types,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            return self.execute(query_built, variables)["hasColumn"]
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_version", id)

    def get_resources_items(
        self, id: str, type: DatasetSourceUsage | None
    ) -> list[DatasetResourceRepresentationOutput]:
        gql_query = "resourcesItems"
        variable_types = "$datasetVersionId:VecticeId!,$resourceType:DatasetSourceUsage"
        kw = "datasetVersionId:$datasetVersionId,resourceType:$resourceType"
        variables = {
            "datasetVersionId": id,
            "resourceType": type,
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_DATASET_SOURCES,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response: Dict[str, Any] = self.execute(query_built, variables)
            dataset_output: list[DatasetResourceRepresentationOutput] = Parser().parse_list(
                reduce(
                    lambda acc, curr: acc
                    + [
                        {
                            **item,
                            "type": curr["type"],
                            "usage": curr.get("usage", None),
                        }
                        for item in (curr["files"]["items"] if curr["type"] == "FILES" else curr["tables"]["items"])
                    ],
                    response[gql_query],
                    [],
                )
            )
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_sources", id)

    def get_columns(self, id: int, type: DatasetSourceType) -> list[Dict[str, Any]]:
        gql_query = "sourceColumns"
        variable_types = "$id:Float!,$columnSourceType:ColumnSourceType!"
        kw = "id:$id,columnSourceType:$columnSourceType"
        variables = {
            "id": id,
            "columnSourceType": "DBColumnSource" if type == DatasetSourceType.DB else "FileSourceColumn",
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_COLUMNS,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return response[gql_query]["items"]
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_sources", id)
