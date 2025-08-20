from __future__ import annotations

import logging

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.public_config import PublicConfigOutput

_logger = logging.getLogger(__name__)

_RETURNS = """
    versions {
        version
        artifactName
    }
    __typename
"""


class VersionApi(GqlApi):
    def get_public_config(self) -> PublicConfigOutput:
        gql_query = "getPublicConfig"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=None,
            returns=_RETURNS,
            keyword_arguments=None,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, None)
            return Parser().parse_item(response[gql_query])
        except TransportQueryError as error:
            raise TransportQueryError("Impossible to get the public configuration.") from error
