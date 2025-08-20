from __future__ import annotations

from typing import Literal

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.gql_model import RETURNS_MODEL_VERSION
from vectice.api.json.issue import IssueOutput
from vectice.api.json.paged_response import PagedResponse
from vectice.utils.api_utils import DEFAULT_NUMBER_OF_ITEMS, PAGINATE_OUTPUT, get_page_input

_RETURNS = """
    id
    name
    severity
    dueDate
    status
    createdDate
    report {
        id
        name
        createdBy {
            name
            email
        }
    }
    owner {
        name
        email
    }
    reviewer {
        name
        email
    }
    __typename
"""

_RETURNS_WITH_MDV = f"""
    {_RETURNS}
    modelVersion {{
        {RETURNS_MODEL_VERSION}
        __typename
    }}
"""

_PAGINATED_ISSUES = PAGINATE_OUTPUT.format(_RETURNS)
_PAGINATED_ISSUES_WITH_MDV = PAGINATE_OUTPUT.format(_RETURNS_WITH_MDV)


class GqlIssueApi(GqlApi):
    def get_issues(
        self, id: str, type: Literal["prj"] | Literal["mdv"], size: int = DEFAULT_NUMBER_OF_ITEMS
    ) -> PagedResponse[IssueOutput]:
        gql_query = "Findings"
        variable_types = "$type:FindingQueryType,$filters:FindingFiltersInput!,$page:PageInput"
        kw = "type:$type,filters:$filters,page:$page"
        kw_name = "projectId" if type == "prj" else "modelVersionId"
        variables = {
            "type": "PROJECT" if type == "prj" else "MODEL_VERSION",
            "filters": {kw_name: id},
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_PAGINATED_ISSUES if type == "mdv" else _PAGINATED_ISSUES_WITH_MDV,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return Parser().parse_paged_response(response[gql_query])
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model_version" if type == "mdv" else "project", id)
