from __future__ import annotations

from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.review import ReviewOutput
from vectice.utils.api_utils import DEFAULT_NUMBER_OF_ITEMS, PAGINATE_OUTPUT, get_page_input

if TYPE_CHECKING:
    from vectice.api.json.paged_response import PagedResponse


_RETURNS = """vecticeId
              status
              feedback
              message
              createdDate
              reviewer {
                name
                email
              }
              createdBy {
                name
                email
              }
              __typename
            """


_RETURNS_PAGE = PAGINATE_OUTPUT.format(_RETURNS)


class GqlReviewApi(GqlApi):
    def list_reviews(self, parent_id: str, size: int = DEFAULT_NUMBER_OF_ITEMS) -> PagedResponse[ReviewOutput]:
        gql_query = "getReviewList"

        variable_types = "$filters:ReviewFiltersInput!,$order:ListOrderInput,$page:PageInput"
        kw = "filters:$filters,order:$order,page:$page"
        variables = {
            "filters": {
                "phaseId": parent_id,
            },
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS_PAGE, keyword_arguments=kw
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            phase_output: PagedResponse[ReviewOutput] = Parser().parse_paged_response(response[gql_query])
            return phase_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", "list")
