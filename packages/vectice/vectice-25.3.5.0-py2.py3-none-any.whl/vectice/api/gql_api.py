from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Type, TypeVar

from gql.graphql_request import GraphQLRequest

from vectice.api.http_error_handlers import ClientErrorHandler
from vectice.api.json import (
    CodeOutput,
    DatasetRegisterOutput,
    IterationOutput,
    IterationStepArtifact,
    ModelRegisterOutput,
    OrgConfigOutput,
    PagedResponse,
    PhaseOutput,
    ProjectOutput,
    ProjectTemplateOutput,
    PublicConfigOutput,
    RequirementOutput,
    SectionOutput,
    UserActivity,
    UserAndDefaultWorkspaceOutput,
    WorkspaceOutput,
)
from vectice.api.json.attachment import AttachmentOutput
from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.api.json.dataset_resource_representation import DatasetResourceRepresentationOutput
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.issue import IssueOutput
from vectice.api.json.iteration import RetrieveIterationOutput
from vectice.api.json.json_type import TJSON
from vectice.api.json.model_representation import ModelRepresentationOutput
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput
from vectice.api.json.report import ReportOutput
from vectice.api.json.review import ReviewOutput

if TYPE_CHECKING:
    from gql import Client
    from gql.transport.requests import RequestsHTTPTransport

    from vectice.api._auth import Auth


ResultType = TypeVar("ResultType")


class Parser(Generic[ResultType]):
    def map_type(self, type_name: str) -> Type[ResultType]:
        types_map = self._build_map()
        if type_name in types_map.keys():
            return types_map[type_name]  # type: ignore[no-any-return]
        else:
            raise RuntimeError("Unknown type: " + type_name)

    def parse_item(self, item: TJSON) -> ResultType:  # type: ignore[type-var]
        clazz: Type[ResultType] = self.map_type(item["__typename"])
        result = clazz(**item)
        return result

    def parse_list(self, list: list[TJSON]) -> list[ResultType]:
        # TODO: rename 'list' parameter to avoid shadowing builtin
        result: List[ResultType] = []
        for item in list:
            result.append(self.parse_item(item))
        return result

    def parse_paged_response(self, data: TJSON) -> PagedResponse[ResultType]:
        return PagedResponse(
            data["total"],
            data["page"],
            self.map_type(data["items"][0]["__typename"]) if len(data["items"]) > 0 else Any,  # type: ignore[arg-type]
            data["items"],
        )

    def parse(self, data: Any) -> ResultType | list[ResultType] | PagedResponse[ResultType]:
        if isinstance(data, list):
            return self.parse_list(data)
        else:
            if "items" in data and "page" in data and "total" in data:
                return self.parse_paged_response(data)
            else:
                return self.parse_item(data)

    def _build_map(self):
        return {
            "Workspace": WorkspaceOutput,
            "Project": ProjectOutput,
            "Phase": PhaseOutput,
            "IterationStep": SectionOutput,
            "Iteration": IterationOutput,
            "RetrieveIterationOutput": RetrieveIterationOutput,
            "IterationStepArtifact": IterationStepArtifact,
            "DatasetRegisterResultOutput": DatasetRegisterOutput,
            "ModelRegisterResultOutput": ModelRegisterOutput,
            "DataSet": DatasetRepresentationOutput,
            "DataSetVersion": DatasetVersionRepresentationOutput,
            "Model": ModelRepresentationOutput,
            "ModelVersion": ModelVersionRepresentationOutput,
            "UserActivity": UserActivity,
            "Code": CodeOutput,
            "PublicConfigOutput": PublicConfigOutput,
            "ProjectTemplateOutput": ProjectTemplateOutput,
            "UserAndDefaultWorkspaceOutput": UserAndDefaultWorkspaceOutput,
            "StepDefinition": RequirementOutput,
            "OrgConfigOutput": OrgConfigOutput,
            "AttachmentOutput": AttachmentOutput,
            "Finding": IssueOutput,
            "CDTReport": ReportOutput,
            "Review": ReviewOutput,
            "FileSource": DatasetResourceRepresentationOutput,
            "DatasetSource": DatasetResourceRepresentationOutput,
            "DBTableSource": DatasetResourceRepresentationOutput,
        }


class GqlApi:
    def __init__(self, client: Client, auth: Auth):
        self.client: Client = client
        self.auth = auth
        self._error_handler = ClientErrorHandler()

    def execute(self, request: GraphQLRequest, variables: Optional[Dict[str, Any]] = None):
        # retrieve auth & api http headers
        transport: RequestsHTTPTransport = self.client.transport  # type: ignore
        transport.headers = self.auth.http_headers
        query = GraphQLRequest(request, variable_values=variables)
        return self.client.execute(query)  # pyright: ignore[reportUnknownMemberType]

    @staticmethod
    def build_query(
        gql_query: str,
        variable_types: str | None = None,
        returns: str | None = None,
        keyword_arguments: str | None = None,
        query: bool = True,
    ):
        query_type = "query" if query else "mutation"
        variable_types_formatted = f"({variable_types})" if variable_types else ""
        keyword_arguments_formatted = f"({keyword_arguments})" if keyword_arguments else ""
        gql_returns = f"{{{returns}}}" if returns else ""
        query_built = f"{query_type} {gql_query} {variable_types_formatted} {{{gql_query} {keyword_arguments_formatted} {gql_returns} }}"
        return query_built
