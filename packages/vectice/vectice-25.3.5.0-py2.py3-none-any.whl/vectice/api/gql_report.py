from __future__ import annotations

from typing import Literal

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.gql_model import RETURNS_MODEL_VERSION
from vectice.api.json.paged_response import PagedResponse
from vectice.api.json.report import ReportOutput
from vectice.utils.api_utils import DEFAULT_NUMBER_OF_ITEMS, PAGINATE_OUTPUT, get_page_input

_RETURNS = f"""
    id
    name
    createdDate
    updatedDate
    createdBy {{
        name
        email
    }}
    modelVersion {{
        {RETURNS_MODEL_VERSION}
        __typename
    }}
    __typename
"""


class GqlReportApi(GqlApi):
    def get_reports(
        self, id: str, type: Literal["prj"] | Literal["mdv"], size: int = DEFAULT_NUMBER_OF_ITEMS
    ) -> PagedResponse[ReportOutput]:
        gql_query = "CDTReports"
        variable_types = "$type:CDTReportQueryType,$filters:CDTReportFiltersInput!,$page:PageInput"
        kw = "type:$type,filters:$filters,page:$page"
        kw_name = "projectId" if type == "prj" else "modelVersionId"
        filters = {kw_name: id}
        variables = {
            "type": "PROJECT" if type == "prj" else "MODEL_VERSION",
            "filters": filters,
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=PAGINATE_OUTPUT.format(_RETURNS),
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return Parser().parse_paged_response(response[gql_query])
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model_version" if type == "mdv" else "project", id)
