from __future__ import annotations

from typing import Any

from vectice import Dataset, DatasetType, FileResource, Table
from vectice.autolog.asset_services.service_types.giskard_types import GiskardType
from vectice.utils.common_utils import temp_directory

GISKARD_TEMP_DIR = "giskard"


class GiskardRAGReportService:
    def __init__(self, key: str, asset: Any):
        self._asset = asset
        self._key = key
        self._temp_dir = temp_directory(GISKARD_TEMP_DIR)

    def _get_rag_metric_tables(self) -> list[Table]:
        tables = []
        # all the pd.DFs from the RAGReport
        correctness_by_question_type = self._asset.correctness_by_question_type()
        tables.append(Table(correctness_by_question_type, "correctness_by_question_type"))
        correctness_by_topic = self._asset.correctness_by_topic()
        tables.append(Table(correctness_by_topic, "correctness_by_topic"))
        component_scores = self._asset.component_scores()
        tables.append(Table(component_scores, "component_scores"))
        failures = self._asset.get_failures()
        tables.append(Table(failures, "get_failures"))
        return tables

    def _get_report_results_as_dataset(self, report_path: str) -> Dataset:
        filename_path = self._temp_dir / "report_dataset.csv"
        filename = filename_path.as_posix()
        # report to pd.DF
        report_df = self._asset.to_pandas()
        report_table = Table(name="Report Table", dataframe=report_df)
        report_df.to_csv(filename)
        resource = FileResource(filename, dataframes=report_df, capture_schema_only=False)
        topics = self._asset.topics
        results_df_name = topics[0] if topics else "Rag Report"
        return Dataset(name=f"{results_df_name} Results", type=DatasetType.UNKNOWN, resource=resource, attachments=[report_table, filename, report_path])  # type: ignore[reportArgumentType]

    def get_asset(self) -> dict[str, Any]:
        assets = {
            "variable": self._key,
            "recommendation": self._asset._recommendation,  # pyright: ignore [reportPrivateUsage]
            "report_dataset": None,
            "tables": self._get_rag_metric_tables(),
            "html": None,
            "all_report_data": None,
            "asset_type": GiskardType.RAG,
        }

        # get all the rag metric tables
        # report html
        report_path = self._temp_dir / "giskard_rag_report.html"
        report_name = report_path.as_posix()
        assets["html"] = report_name
        self._asset.to_html(report_name)
        # get the rag report results as a Dataset with attachments
        assets["report_dataset"] = self._get_report_results_as_dataset(report_name)  # type: ignore[reportArgumentType]
        return assets
