from __future__ import annotations

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json import OrgConfigOutput

_RETURNS = """
    organization {
        configuration {
            dfStatisticsRowThreshold
            dfStatisticsSampleRows
            dfStatisticsMaxColumns
        }
    }
    __typename
"""


class GqlOrganizationApi(GqlApi):
    def get_organization_config(self) -> OrgConfigOutput:
        query = GqlApi.build_query(
            gql_query="getOrgConfig",
            returns=_RETURNS,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built)
            output: OrgConfigOutput = Parser().parse_item(response["getOrgConfig"])
            return output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "code", "getOrgConfig")
