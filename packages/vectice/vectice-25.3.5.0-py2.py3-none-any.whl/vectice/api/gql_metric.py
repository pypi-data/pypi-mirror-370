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


class GqlMetricApi(GqlApi):
    def upsert(
        self, type: str, id: str, metrics: list[dict[str, str | float | int]]
    ) -> list[dict[str, str | int | float]]:
        variable_types = (
            "$entityType:EntityMetricType!,$entityId:VecticeId!,$upsertMetricList:[UpsertEntityMetricInput!]!"
        )
        kw = "entityType:$entityType,entityId:$entityId,upsertMetricList:$upsertMetricList"
        variables = {"entityType": type, "entityId": id, "upsertMetricList": metrics}
        gql_query = "upsertEntityMetrics"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        return self.execute(query_built, variables)[gql_query]["items"]
