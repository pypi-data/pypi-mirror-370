from __future__ import annotations

import re
from typing import TYPE_CHECKING

from gql import gql

from vectice.api.json.paged_response import PagedResponse
from vectice.utils.api_utils import DEFAULT_NUMBER_OF_ITEMS, PAGINATE_OUTPUT, get_page_input
from vectice.utils.vectice_ids_regex import WORKSPACE_VID_REG

if TYPE_CHECKING:
    from vectice.api.json import WorkspaceOutput

from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser

_RETURNS = """
            name
            description
            vecticeId
            __typename
"""

_RETURNS_PAGE = PAGINATE_OUTPUT.format(_RETURNS)


class WorkspaceApi(GqlApi):
    def get_workspace(self, workspace: str) -> WorkspaceOutput:
        search_vectice_id = re.search(WORKSPACE_VID_REG, workspace)
        if search_vectice_id:
            gql_query = "getWorkspaceById"
            variable_types = "$workspaceId:VecticeId!"
            variables = {"workspaceId": workspace}
            kw = "workspaceId:$workspaceId"
        else:
            gql_query = "getWorkspaceByName"
            variable_types = "$name:String!"
            variables = {"name": workspace}
            kw = "name:$name"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            workspace_output: WorkspaceOutput = Parser().parse_item(response[gql_query])
            return workspace_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "workspace", workspace)

    def list_workspaces(self, size: int = DEFAULT_NUMBER_OF_ITEMS) -> PagedResponse[WorkspaceOutput]:
        gql_query = "getUserWorkspaceList"
        variable_types = "$page: PageInput!"
        variables = {"page": get_page_input(size=size)}
        kw = "page:$page"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_PAGE,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            workspace_output: PagedResponse[WorkspaceOutput] = Parser().parse_paged_response(response[gql_query])
            return workspace_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "workspaces", "list")
