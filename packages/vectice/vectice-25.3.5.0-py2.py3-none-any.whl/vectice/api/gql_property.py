from __future__ import annotations

from gql import gql

from vectice.api.gql_api import GqlApi
from vectice.utils.api_utils import PAGINATE_OUTPUT

_RETURNS = PAGINATE_OUTPUT.format(
    """
    key
    value
    __typename
"""
)


class GqlPropertyApi(GqlApi):
    def upsert(self, type: str, id: str, properties: list[dict[str, str | int]]) -> list[dict[str, str | int]]:
        variable_types = (
            "$entityType:EntityPropertyType!,$entityId:VecticeId!,$upsertPropertyList:[UpsertEntityPropertyInput!]!"
        )
        kw = "entityType:$entityType,entityId:$entityId,upsertPropertyList:$upsertPropertyList"
        variables = {"entityType": type, "entityId": id, "upsertPropertyList": properties}
        gql_query = "upsertEntityProperties"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        return self.execute(query_built, variables)[gql_query]["items"]
