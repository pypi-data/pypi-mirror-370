from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.iteration import (
    IterationStatus,
    IterationStepArtifact,
    IterationStepArtifactInput,
    IterationUpdateInput,
    RetrieveIterationOutput,
)
from vectice.api.json.json_type import TJSON
from vectice.api.json.paged_response import PagedResponse
from vectice.types.iteration import IterationInput
from vectice.utils.api_utils import (
    DEFAULT_NUMBER_OF_ITEMS,
    INDEX_ORDERED,
    INDEX_ORDERED_DESC,
    PAGINATE_OUTPUT,
    get_page_input,
)

if TYPE_CHECKING:
    from vectice.api.json.iteration import IterationContextInput, IterationOutput
    from vectice.api.json.report import ReportOutput

_logger = logging.getLogger(__name__)

_RETURNS_LIST = """vecticeId
            index
            name
            description
            status
            owner {
                id
                name
            }
            starred
            __typename
            """

_RETURNS_PAGE = PAGINATE_OUTPUT.format(_RETURNS_LIST)

_BASE_RETURNS = """
            vecticeId
            index
            name
            description
            status
            starred
            __typename
            """
_BASE_PARENT = """
            phase {
                    vecticeId
                    name
                    status
                    index
                    __typename
              }
"""

_RETURNS = f"""
    {_BASE_RETURNS}
    {_BASE_PARENT}
"""

_RETURN_GET_OR_CREATE_ITERATION = f"""
            iteration {{
                {_BASE_RETURNS}
                {_BASE_PARENT}
                }}
            useExistingIteration
            __typename
            """

_PARENT_FULL = """
            phase {
                    vecticeId
                    name
                    status
                    index
                    __typename
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
              }
"""

_RETURNS_FULL = f"""
    {_BASE_RETURNS}
    {_PARENT_FULL}
"""

_RETURNS_ARTIFACT = """
            iterationId
            __typename
"""

_RETURNS_LIST_SECTIONS = """
    paginatedArtifacts {
        items {
            id
        }
        total
    }
    sections(page: $page, order: $order) {
        items {
            name
            paginatedArtifacts {
                items {
                    id
                }
                total
            }
            __typename
        }
        page {
            index
            size
        }
        total
        __typename
    }
    __typename
"""

_RETURNS_ASSET = PAGINATE_OUTPUT.format(
    """
    id
    index
    type
    text
    datasetVersionId
    modelVersionId
    entityFileId
    entityMetadataId
    modelVersion {
        vecticeId
        name
        __typename
    }
    datasetVersion {
        vecticeId
        name
        __typename
    }
    entityFile {
        id
        fileName
        __typename
    }
    entityMetadata {
        id
        name
        __typename
    }
    step {
        name
        __typename
    }
    __typename
"""
)

_RETURNS_LIST_ASSETS = f"""
    {_BASE_RETURNS}
    paginatedArtifacts(filters: $filters) {{
        {_RETURNS_ASSET}
        __typename
    }}
"""


_RETURNS_ORGANIZE = """
    id
    __typename
"""

_RETURNS_ORGANIZE_AND_REPORT = """
    id
    name
    __typename
"""


class IterationApi(GqlApi):
    def list_iterations(
        self,
        parent_id: str,
        only_mine: bool = False,
        statuses: list[IterationStatus] | None = None,
        size: int = DEFAULT_NUMBER_OF_ITEMS,
    ) -> PagedResponse[IterationOutput]:
        gql_query = "getIterationList"
        filters = {
            "phaseId": parent_id,
            "onlyMine": only_mine,
            "status": (
                list(map(lambda status: status.value, statuses)) if statuses is not None and len(statuses) > 0 else None
            ),
        }

        variable_types = "$filters:IterationFiltersInput!,$order:ListOrderInput,$page:PageInput"
        kw = "filters:$filters,order:$order,page:$page"
        variables = {
            "filters": filters,
            "order": INDEX_ORDERED_DESC,
            "page": get_page_input(size=size),
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_PAGE,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iterations_output: PagedResponse[IterationOutput] = Parser().parse_paged_response(response[gql_query])
            return iterations_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", "list")

    def list_iteration_assets(self, id: str) -> PagedResponse[IterationStepArtifact]:
        gql_query = "getIterationById"
        variable_types = "$id:VecticeId!,$filters:IterationArtifactsFiltersInput!"
        variables = {"id": id, "filters": {"stepStrategy": "INCLUDES"}}
        kw = "id:$id"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_LIST_ASSETS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            assets: PagedResponse[IterationStepArtifact] = Parser().parse_paged_response(
                response[gql_query]["paginatedArtifacts"]
            )
            return assets
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", "list_assets")

    def create_iteration(self, phase_id: str, iteration: IterationInput | None = None) -> IterationOutput:
        gql_query = "createIteration"
        variable_types = "$phaseId:VecticeId!,$data:IterationCreateInput"
        variables = {"phaseId": phase_id, "data": iteration}
        kw = "phaseId:$phaseId,data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=False
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", phase_id)

    def get_last_iteration(self, phase_id: str, iteration: IterationInput | None = None) -> RetrieveIterationOutput:
        gql_query = "retrieveIteration"
        variable_types = "$phaseId:VecticeId!,$data:IterationCreateInput"
        variables = {"phaseId": phase_id, "data": iteration}
        kw = "phaseId:$phaseId,data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURN_GET_OR_CREATE_ITERATION,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return Parser().parse_item(response[gql_query])
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", phase_id)

    def get_active_iteration_or_create(self, phase_id: str, iteration: IterationInput | None = None) -> IterationOutput:
        gql_query = "getActiveIterationOrCreateOne"
        variable_types = "$phaseId:VecticeId!,$data:IterationCreateInput"
        variables = {"phaseId": phase_id, "data": iteration}
        kw = "phaseId:$phaseId,data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return Parser().parse_item(response[gql_query])
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", phase_id)

    def get_iteration_by_id(self, iteration_id: str, full: bool = False) -> IterationOutput:
        gql_query = "getIterationById"
        variable_types = "$id:VecticeId!"
        variables = {"id": iteration_id}
        kw = "id:$id"
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
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def get_iteration_by_index(self, phase_id: str, index: int) -> IterationOutput:
        gql_query = "getIterationByIndex"
        variable_types = "$index:Float!,$phaseId:VecticeId!"
        variables = {"index": index, "phaseId": phase_id}
        kw = "index:$index,phaseId:$phaseId"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration_index", index)

    def update_iteration(self, iteration: IterationUpdateInput, iteration_id: str) -> IterationOutput:
        variable_types = "$id:VecticeId!,$data:IterationUpdateInput!"
        kw = "id:$id,data:$data"
        variables = {"id": iteration_id, "data": iteration}
        query = GqlApi.build_query(
            gql_query="updateIteration",
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response["updateIteration"])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", "put")

    def delete_iteration(self, iteration_id: str) -> None:
        variable_types = "$id:VecticeId!"
        kw = "id:$id"
        variables = {"id": iteration_id}
        query = GqlApi.build_query(
            gql_query="removeIteration",
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def add_iteration_artifacts(
        self,
        artifacts: list[IterationStepArtifactInput],
        iteration_context: IterationContextInput,
    ) -> list[IterationStepArtifact]:
        gql_query = "addIterationContent"
        variable_types = "$artifacts:[IterationStepArtifactInput!]!, $iterationContext:IterationContextInput!"
        variables: dict[str, Any] = {"artifacts": artifacts, "iterationContext": iteration_context}
        kw = "artifacts:$artifacts, iterationContext:$iterationContext"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_ARTIFACT,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response: list[TJSON] = self.execute(query_built, variables)["addIterationContent"]
            iteration_output: list[IterationStepArtifact] = Parser().parse_list(response)
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_context.id)

    def remove_iteration_assets(
        self,
        iteration_context: IterationContextInput,
        all: bool,
    ):
        gql_query = "removeIterationAssets"
        variable_types = "$data:IterationRemoveAssetsInput!"
        variables: dict[str, Any] = {"data": {**iteration_context, "all": all}}
        kw = "data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(
                e,
                "section" if iteration_context.section else "iteration",
                iteration_context.section or iteration_context.id,
            )

    def remove_assets_from_iteration(
        self,
        iteration_id: str,
        artifacts_id_list: list[int],
    ):
        gql_query = "removeAssetsFromIteration"
        variable_types = "$artifactsIdList:[Float!]!, $iterationId:VecticeId!"
        variables: dict[str, Any] = {"artifactsIdList": artifacts_id_list, "iterationId": iteration_id}
        kw = "artifactsIdList:$artifactsIdList, iterationId:$iterationId"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def list_sections(self, iteration_id: str) -> IterationOutput:
        gql_query = "getIterationById"
        variable_types = "$id:VecticeId!,$page:PageInput,$order:ListOrderInput"
        variables = {"id": iteration_id, "page": get_page_input(), "order": INDEX_ORDERED}
        kw = "id:$id"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_LIST_SECTIONS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def save_autolog_cells(
        self, iteration_id: str, cells: list[dict[str, str]], prefix: str | None = None, is_trace: bool = False
    ):
        gql_query = "saveAutologCells"
        variable_types = "$cells:[AutologCellInput!]!, $iterationId:VecticeId!, $prefix: String, $isTrace: Boolean"
        variables: dict[str, Any] = {"cells": cells, "iterationId": iteration_id, "prefix": prefix, "isTrace": is_trace}
        kw = "cells:$cells, iterationId:$iterationId, prefix:$prefix, isTrace:$isTrace"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def organize_with_ai(self, iteration_id: str):
        gql_query = "generateIterationContent"
        variable_types = "$iterationId:VecticeId!"
        variables: dict[str, Any] = {"iterationId": iteration_id}
        kw = "iterationId:$iterationId"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
            returns=_RETURNS_ORGANIZE,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def organize_with_ai_and_report(self, iteration_id: str) -> ReportOutput:
        gql_query = "generateIterationContentAndReport"
        variable_types = "$iterationId:VecticeId!"
        variables: dict[str, Any] = {"iterationId": iteration_id}
        kw = "iterationId:$iterationId"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
            returns=_RETURNS_ORGANIZE_AND_REPORT,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            report_output: ReportOutput = Parser().parse_item(response["generateIterationContentAndReport"])
            return report_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)
