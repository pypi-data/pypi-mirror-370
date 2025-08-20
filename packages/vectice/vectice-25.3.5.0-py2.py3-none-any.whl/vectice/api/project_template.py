from __future__ import annotations

from typing import TYPE_CHECKING

from gql import gql

if TYPE_CHECKING:
    from vectice.api.json import ProjectTemplateOutput

from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser

_RETURNS = """
            name
            description
            __typename
"""


class ProjectTemplateApi(GqlApi):
    def list_templates(self) -> list[ProjectTemplateOutput]:
        gql_query = "getProjectTemplateList"
        query = GqlApi.build_query(
            gql_query=gql_query,
            returns=_RETURNS,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built)
            output: list[ProjectTemplateOutput] = Parser().parse_list(response[gql_query])
            return output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "workspace", "list")
