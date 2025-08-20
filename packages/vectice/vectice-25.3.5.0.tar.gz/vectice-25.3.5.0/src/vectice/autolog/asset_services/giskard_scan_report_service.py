from __future__ import annotations

from typing import Any

from vectice import Dataset, DatasetType, FileResource, Table
from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.property_service import PropertyService
from vectice.autolog.asset_services.service_types.giskard_types import GiskardType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.utils.common_utils import temp_directory

GISKARD_TEMP_DIR = "giskard"


class GiskardScanReportService(PropertyService, MetricService, TechniqueService):
    def __init__(self, key: str, asset: Any, data: dict):
        self._asset = asset
        self._key = key
        self._temp_dir = temp_directory(GISKARD_TEMP_DIR)

        super().__init__(cell_data=data)

    def _get_rag_model_info(self, model: Any, model_meta: Any) -> dict:
        # predictive function
        params = model_meta.__dict__

        def parse_dict_with_objects_flat(input_dict: dict, prefix: str = "", seen: set | None = None):
            if seen is None:
                seen = set()

            result = {}

            def process_item(key: str, value: dict | Any, current_prefix: str):
                new_key = f"{current_prefix}_{key}" if current_prefix else key

                if isinstance(value, dict):
                    result.update(parse_dict_with_objects_flat(value, f"{new_key}", seen))
                elif hasattr(value, "__dict__"):
                    if id(value) not in seen:
                        seen.add(id(value))
                        class_name = value.__class__.__name__
                        result.update(parse_dict_with_objects_flat(value.__dict__, f"{new_key}_{class_name}", seen))
                        seen.remove(id(value))
                else:
                    result[new_key] = value

            for key, value in input_dict.items():
                process_item(key, value, prefix)

            return result

        parsed_dict = parse_dict_with_objects_flat(params)

        return {
            "variable": self._key,
            "model": model,
            "name": parsed_dict["name"],
            "properties": parsed_dict,
        }

    def _parse_issues(self, issues: list[Any]) -> list[Table]:
        # issues are in groups e.g harmfulness, have a level e.g medium and examples in a pd.DF
        parsed_issues = []

        for issue in issues:
            format_issue = {"section": issue.group.name, "section_description": issue.group.description}
            format_issue["level"] = f"level {issue.level.value}:\n{issue.description}"
            format_issue["table"] = Table(name=f"{issue.group.name} Examples", dataframe=issue.examples(n=5))
            parsed_issues.append(format_issue)
        return parsed_issues

    def _get_report_results_as_dataset(self, report_path: str) -> Dataset:
        filename_path = self._temp_dir / "results_dataset.csv"
        filename = filename_path.as_posix()

        # results df
        results_df = self._asset.to_dataframe()
        results_table = Table(name="Results Table", dataframe=results_df)
        results_df.to_csv(filename)
        resource = FileResource(filename, dataframes=results_df, capture_schema_only=False)
        results_df_name = self._asset.model.name or self._asset.dataset.name
        return Dataset(name=f"{results_df_name} Results", type=DatasetType.UNKNOWN, resource=resource, attachments=[results_table, filename, report_path])  # type: ignore[reportArgumentType]

    def get_asset(self) -> dict[str, Any]:
        asset = {
            "variable": self._key,
            "dataset": None,
            "model": None,
            "scan_report": None,
            "issues": [],
            "asset_type": GiskardType.SCAN,
        }
        # get report html
        report_path = self._temp_dir / "giskard_scan_report.html"
        report_name = report_path.as_posix()
        asset["scan_report"] = report_name
        self._asset.to_html(report_name)
        # input dataset
        asset["input_table"] = Table(name="Question Test Set", dataframe=self._asset.dataset.df)  # type: ignore[reportArgumentType]
        # get the scanner report results as a Dataset with attachments
        asset["results_dataset"] = self._get_report_results_as_dataset(report_name)  # type: ignore[reportArgumentType]
        # parse issues
        asset["issues"] = self._parse_issues(self._asset.issues)

        return asset
