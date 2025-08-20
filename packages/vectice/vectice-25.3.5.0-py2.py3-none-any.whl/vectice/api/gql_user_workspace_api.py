from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser

if TYPE_CHECKING:
    from vectice.api.json.user_and_workspace import UserAndDefaultWorkspaceOutput

_logger = logging.getLogger(__name__)

_RETURNS = """
                user{
                    name
                }
                defaultWorkspace{
                                vecticeId
                }
                __typename
"""


class UserAndDefaultWorkspaceApi(GqlApi):
    def get_user_and_default_workspace(self):
        query = GqlApi.build_query(
            gql_query="whoAmI",
            variable_types=None,
            returns=_RETURNS,
            keyword_arguments=None,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built)
            assets_output: UserAndDefaultWorkspaceOutput = Parser().parse_item(response["whoAmI"])
            return assets_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "asset", "whoAmI")
