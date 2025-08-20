from __future__ import annotations

from typing import Any, Literal

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.attachment import AttachmentOutput
from vectice.api.json.iteration import IterationStepArtifactEntityMetadataInput
from vectice.models.table import Table
from vectice.utils.dataframe_utils import transform_table_to_metadata_dict

_RETURNS_UPSERT = """
            name
            __typename
            """

_RETURNS = """
            id
            name
            attachmentType
            __typename
            """


class GqlAttachmentApi(GqlApi):
    def upsert(
        self, entity_id: str, entity_type: Literal["DATASET_VERSION"] | Literal["MODEL_VERSION"], tables: list[Table]
    ):
        def serialize_table(asset: Table):
            data = transform_table_to_metadata_dict(asset)
            return IterationStepArtifactEntityMetadataInput(name=asset.name, content={"data": data})

        gql_query = "upsertEntityMetadata"
        variable_types = "$entityId:VecticeId!,$entityType:EntityMetadataTypeEnum!,$data:[EntityMetadataCreateInput!]!"
        kw = "entityId:$entityId,entityType:$entityType,data:$data"
        variables = {"entityId": entity_id, "entityType": entity_type, "data": list(map(serialize_table, tables))}
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_UPSERT,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            return self.execute(query_built, variables)[gql_query]
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "attachment", "upsert")

    def attach_file_to_lineage(self, lineage_id: int, entity_file_id: int):
        gql_query = "attachFileToLineage"
        variable_types = "$lineageId:Float!,$entityFileId:Float!"
        kw = "lineageId:$lineageId,entityFileId:$entityFileId"
        variables = {"lineageId": lineage_id, "entityFileId": entity_file_id}
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=None,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            return self.execute(query_built, variables)[gql_query]
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "attachment", "attach")

    def get_version_table(
        self,
        entity_id: str,
        entity_type: Literal["DATASET_VERSION"] | Literal["MODEL_VERSION"] | Literal["ITERATION"],
        table: str,
    ) -> dict[str, Any]:
        gql_query = "entityMetadataContent"
        variable_types = "$entityId:VecticeId!,$entityType:EntityMetadataTypeEnum!,$table:String!"
        kw = "entityId:$entityId,entityType:$entityType,table:$table"
        variables = {"entityId": entity_id, "entityType": entity_type, "table": table}
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=None,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            return self.execute(query_built, variables)[gql_query]
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "attachment", "get table")

    def list_attachments(
        self,
        entity_id: str,
        entity_type: Literal["DATASET_VERSION"] | Literal["MODEL_VERSION"] | Literal["ITERATION"],
    ) -> list[AttachmentOutput]:
        gql_query = "attachments"
        variable_types = "$entityId:VecticeId!,$entityType:EntityMetadataTypeEnum!"
        kw = "entityId:$entityId,entityType:$entityType"
        variables = {"entityId": entity_id, "entityType": entity_type}
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            return Parser().parse_list(self.execute(query_built, variables)[gql_query])
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "attachment", "list")
