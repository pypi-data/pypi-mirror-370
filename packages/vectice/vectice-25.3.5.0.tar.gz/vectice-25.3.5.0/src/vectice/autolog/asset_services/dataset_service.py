from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

from vectice.utils.code_parser import FilePathVisitor, preprocess_code
from vectice.utils.common_utils import get_asset_name

if TYPE_CHECKING:
    from h2o.frame import H2OFrame  # type: ignore[reportMissingImports]
    from pandas import DataFrame
    from pyspark.sql import DataFrame as SparkDF
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDF

    from vectice.models.resource.metadata.db_metadata import TableType


class DatasetService:
    def __init__(self, raw_cells_data: list[str], capture_schema_only: bool):
        self._raw_cells_data = raw_cells_data
        self._capture_schema_only = capture_schema_only

    def _create_vectice_dataset(
        self,
        dataset: DataFrame | SparkConnectDF | SparkDF | H2OFrame,  # type: ignore[reportMissingImports]
        phase_name: str,
        key: str,
        table_type: TableType,
        prefix: str | None = None,
    ):
        from vectice import Dataset, DatasetType, FileResource, NoResource

        resource = self._get_dataset_resource(key)
        dataset_name = get_asset_name(key, phase_name, prefix)
        no_resource_dataset = Dataset(
            type=DatasetType.UNKNOWN,
            resource=NoResource(
                dataframes=dataset,
                origin="DATAFRAME",
                type=table_type,
                capture_schema_only=self._capture_schema_only,
            ),
            name=dataset_name,
        )
        if resource:
            # TODO Dataset type ?
            vec_dataset = Dataset(
                type=DatasetType.UNKNOWN,
                resource=FileResource(
                    paths=resource,
                    dataframes=dataset,
                    capture_schema_only=self._capture_schema_only,
                ),
                name=dataset_name,
            )
        else:
            vec_dataset = no_resource_dataset
        return vec_dataset

    def _get_dataset_resource(self, key: str) -> str | None:
        if not self._raw_cells_data:
            return None
        try:
            # Avoid getting stray dataset with autolog.notebook()

            match = []
            for cell in self._raw_cells_data:
                cell = preprocess_code(cell)
                tree = ast.parse(cell)
                visitor = FilePathVisitor(is_dataset_path=True)
                visitor.visit(tree)
                for resource_info in visitor.dataset_file_paths:
                    path_var, file_path = resource_info["variable"], resource_info["path"]
                    dataset_variable = re.escape(key)
                    if path_var:
                        pattern = rf"{dataset_variable}\s*=\s*pd\.read_csv\(\s*{path_var}\s*\).*\n"
                    else:
                        regex_path = re.escape(file_path)
                        pattern = rf"{dataset_variable}\s*=\s*pd\.read_csv\(.*?{regex_path}.*?\).*\n"
                    match_dataset_path = re.search(pattern, cell)
                    if match_dataset_path:
                        match.append(file_path)

            if len(match) < 1:
                return None
            # TODO update regex
            # check if read csv has comma dominated arguments
            return match[0]
        except TypeError:
            return None
