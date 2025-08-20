from __future__ import annotations

import re
from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.types.phase import PhaseInput
from vectice.utils.api_utils import DEFAULT_NUMBER_OF_ITEMS, INDEX_ORDERED, PAGINATE_OUTPUT, get_page_input
from vectice.utils.vectice_ids_regex import PHASE_VID_REG

if TYPE_CHECKING:
    from vectice.api.json.paged_response import PagedResponse
    from vectice.api.json.phase import PhaseOutput
    from vectice.api.json.requirement import RequirementOutput


_RETURNS = """vecticeId
              name
              status
              index
              owner {
                name
              }
              __typename
            """

_RETURNS_LIST = f"""
    {_RETURNS}
    iterationsCount {{
        notStarted
        inProgress
        inReview
        total
    }}
    stepsCount
"""

_RETURNS_PAGE = PAGINATE_OUTPUT.format(_RETURNS_LIST)

_PARENT_FULL = """
                parent {
                    vecticeId
                    name
                    description
                    workspace {
                        vecticeId
                        name
                        description
                        __typename
                    }
                    __typename
                }
"""

_RETURNS_FULL = f"""
    {_RETURNS}
    {_PARENT_FULL}
"""

_STEP_DEFINITION_RETURNS = """
    items {
        name
        description
        __typename
    }
    total
    page {
        index
        size
    }
    __typename
"""


class GqlPhaseApi(GqlApi):
    def list_phases(self, parent_id: str, size: int = DEFAULT_NUMBER_OF_ITEMS) -> PagedResponse[PhaseOutput]:
        gql_query = "getPhaseList"

        variable_types = "$filters:PhaseFiltersInput!,$order:ListOrderInput,$page:PageInput"
        kw = "filters:$filters,order:$order,page:$page"
        variables = {
            "filters": {
                "parentId": parent_id,
            },
            "order": INDEX_ORDERED,
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS_PAGE, keyword_arguments=kw
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            phase_output: PagedResponse[PhaseOutput] = Parser().parse_paged_response(response[gql_query])
            return phase_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", "list")

    def get_phase(self, phase: str, parent_id: str | None = None, full: bool = False) -> PhaseOutput:
        if re.search(PHASE_VID_REG, phase):
            gql_query = "getPhaseById"
            variable_types = "$id:VecticeId!"
            variables = {"id": phase}
            kw = "id:$id"
        elif parent_id:
            gql_query = "getPhaseByName"
            variable_types = "$name:String!,$parentId:VecticeId!"
            variables = {"name": phase, "parentId": parent_id}
            kw = "name:$name,parentId:$parentId"
        else:
            raise ValueError("Missing parameters: string and parent id required.")
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_FULL if full else _RETURNS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            phase_output: PhaseOutput = Parser().parse_item(response[gql_query])
            return phase_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", phase)

    def create_phase(self, project_id: str, phase: PhaseInput) -> PhaseOutput:
        gql_query = "createPhase"
        variable_types = "$createModel:PhaseCreateInput!,$parentId:VecticeId!"
        variables = {
            "createModel": phase,
            "parentId": project_id,
        }
        kw = "createModel:$createModel,parentId:$parentId"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=False
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            phase_output: PhaseOutput = Parser().parse_item(response[gql_query])
            return phase_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", project_id)

    def list_step_definitions(self, parent_id: str) -> PagedResponse[RequirementOutput]:
        gql_query = "getStepDefinitionList"
        alias_filter = {"parentId": parent_id}
        returns = _STEP_DEFINITION_RETURNS
        variable_types = "$filters:BaseDocumentationListFiltersInput!,$order:ListOrderInput,$page:PageInput"
        kw = "filters:$filters,order:$order,page:$page"
        variables = {
            "filters": alias_filter,
            "order": INDEX_ORDERED,
            "page": get_page_input(),
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=returns,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            requirements: PagedResponse[RequirementOutput] = Parser().parse_paged_response(response[gql_query])
            return requirements
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", "list")
