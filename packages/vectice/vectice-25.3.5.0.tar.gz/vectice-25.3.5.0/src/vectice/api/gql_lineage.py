from __future__ import annotations

from typing import Literal

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.gql_dataset import RETURNS_DATASET_VERSION
from vectice.api.gql_model import RETURNS_MODEL_VERSION
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput

_RETURNS_INPUTS = f"""
    vecticeId
    inputs {{
        {RETURNS_DATASET_VERSION}
        __typename
    }}
    __typename
"""

_RETURNS_CHILDREN = f"""
    vecticeId
    children {{
        modelVersions {{
            {RETURNS_MODEL_VERSION}
            __typename
        }}
        datasetVersions {{
            {RETURNS_DATASET_VERSION}
            __typename
        }}
        __typename
    }}
    __typename
"""


class GqlLineageApi(GqlApi):
    def get_lineage_inputs(
        self, id: str, type: Literal["dtv"] | Literal["mdv"]
    ) -> list[DatasetVersionRepresentationOutput]:
        gql_query = "getModelVersion" if type == "mdv" else "getDatasetVersion"
        kw_name = "modelVersionId" if type == "mdv" else "datasetVersionId"
        variable_types = f"${kw_name}:VecticeId!"
        kw = f"{kw_name}:${kw_name}"
        variables = {kw_name: id}
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_INPUTS,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return Parser().parse_list(response[gql_query]["inputs"])
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model_version" if type == "mdv" else "dataset_version", id)

    def get_lineage_children(self, id: str, type: Literal["dtv"] | Literal["mdv"]) -> tuple[
        list[ModelVersionRepresentationOutput],
        list[DatasetVersionRepresentationOutput],
    ]:
        gql_query = "getModelVersion" if type == "mdv" else "getDatasetVersion"
        kw_name = "modelVersionId" if type == "mdv" else "datasetVersionId"
        variable_types = f"${kw_name}:VecticeId!"
        kw = f"{kw_name}:${kw_name}"
        variables = {kw_name: id}
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_CHILDREN,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            return Parser().parse_list(response[gql_query]["children"]["modelVersions"]), Parser().parse_list(
                response[gql_query]["children"]["datasetVersions"]
            )
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model_version" if type == "mdv" else "dataset_version", id)
