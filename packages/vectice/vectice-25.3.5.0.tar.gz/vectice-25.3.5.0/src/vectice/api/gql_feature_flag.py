from __future__ import annotations

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi


class GqlFeatureFlagApi(GqlApi):
    def is_feature_flag_enabled(
        self,
        code: str,
    ) -> bool:
        variable_types = "$code:String!"
        kw = "code:$code"
        variables = {"code": code}

        query = GqlApi.build_query(
            gql_query="isFeatureFlagEnabled",
            variable_types=variable_types,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return response["isFeatureFlagEnabled"]  # type: ignore[no-any-return]
        except TransportQueryError:
            return True
