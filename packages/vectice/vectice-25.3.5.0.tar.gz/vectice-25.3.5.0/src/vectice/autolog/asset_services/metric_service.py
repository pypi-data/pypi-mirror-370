from __future__ import annotations

import ast
import math
import re
from functools import reduce
from typing import TYPE_CHECKING, Any

from vectice import Table
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.utils.code_parser import VariableVisitor, preprocess_code

if TYPE_CHECKING:
    from keras.models import Model as KerasModel  # type: ignore[reportMissingImports]
    from numpy import float_
    from statsmodels.base.wrapper import ResultsWrapper


captured_metrics = set()

# basic metrics
_autolog_metric_allowlist = [
    "aic",
    "bic",
    "centered_tss",
    "condition_number",
    "df_model",
    "df_resid",
    "ess",
    "f_pvalue",
    "fvalue",
    "llf",
    "mse_model",
    "mse_resid",
    "mse_total",
    "rsquared",
    "rsquared_adj",
    "scale",
    "ssr",
    "uncentered_tss",
]


class MetricService:
    def __init__(self, cell_data: dict, custom_metrics: set[str | None] = set()):
        self._cell_data = cell_data
        self._model_cell = None
        self._custom_metrics = custom_metrics

    def _get_metrics(self, cell_content: str) -> list[str]:
        # Get model cell content for metrics
        self._model_cell = preprocess_code(cell_content)

        tree = ast.parse(self._model_cell)
        visitor = VariableVisitor(True, self._custom_metrics)
        visitor.visit(tree)

        return list(visitor.metric_variables)

    def _get_model_metrics(self, data: dict) -> dict[str, Any]:
        cell_content = data["cell"]
        variables = data["variables"]

        if not cell_content:
            return {}

        metric_variables = self._get_metrics(cell_content)
        metrics = reduce(
            lambda identified_metrics, key: (
                {**identified_metrics, key: variables[key]}
                if key in metric_variables and isinstance(variables[key], (int, float))
                else identified_metrics
            ),
            variables.keys(),
            {},
        )
        captured_metrics.update(list(metrics.keys()))
        return metrics

    def get_assets(self):
        metric_tables = self._get_metric_tables(self._cell_data)
        key = "_".join([table.name for table in metric_tables if table is not None])
        return {
            "variable": key,
            "tables": metric_tables,
            "asset_type": VecticeType.METRIC,
        }

    def _get_metric_tables(self, data: dict) -> list[Table | None]:
        cell_content = data["cell"]
        variables = data["variables"]

        if not cell_content:
            return []

        metric_variables = self._get_metrics(cell_content)
        metric_tables = reduce(
            lambda identified_metrics, key: (
                [*identified_metrics, self._parse_metric_table(variables[key], key)]
                if key in metric_variables and isinstance(variables[key], (str, dict)) and key not in captured_metrics
                else identified_metrics
            ),
            variables.keys(),
            [],
        )
        captured_metrics.update([table.name for table in metric_tables if table is not None])
        return metric_tables

    def _parse_metric_table(self, metric_data: str | dict[str, Any], key: str) -> Table | None:
        from pandas import DataFrame

        if isinstance(metric_data, dict):
            return Table(DataFrame(metric_data), key)
        data = self._parse_classification_report(metric_data)
        if data is not None:
            return Table(data, key)
        return None

    def _parse_classification_report(self, report: str):
        from pandas import DataFrame

        lines = report.split("\n")  # Preserve exact structure
        if not lines:
            return None

        # Extract headers
        headers = re.split(r"\s{2,}", lines[0].strip())
        headers.insert(0, "\u00a0")  # Add leading column for labels
        num_columns = len(headers)

        # Process rows
        data = []
        for line in lines[1:]:
            if line.strip():  # Non-empty row
                rows = re.split(r"\s{2,}", line.strip())
                if len(rows) < num_columns:
                    # Rows like 'accuracy' should have placeholders in the beginning
                    rows = [rows[0]] + ["\u00a0"] * (num_columns - len(rows)) + rows[1:]
                data.append(rows)
            else:  # Empty row
                data.append(["\u00a0"] * num_columns)  # Insert a whitespace row

        # Create DataFrame
        df = DataFrame(data, columns=headers)
        return df

    def _get_keras_training_metrics(self, model: KerasModel) -> dict[str, float]:
        try:
            return {
                str(key)
                + "_train": float(model.get_metrics_result()[key].numpy())  # pyright: ignore[reportGeneralTypeIssues]
                for key in model.get_metrics_result().keys()  # pyright: ignore[reportGeneralTypeIssues]
            }
        except Exception:
            return {}

    def _get_statsmodels_metrics(self, model: ResultsWrapper):
        try:
            # statsmodels can function without numpy
            import numpy

            has_numpy = True
        except ImportError:
            has_numpy = False

        def _convert_metric(metric_value: float | float_) -> float | None:
            if metric_value is numpy.float_:  # pyright: ignore[reportPossiblyUnboundVariable]
                metric_value = metric_value.item()

            if math.isnan(float(metric_value)):
                return None
            return round(float(metric_value), 4)

        result_metrics = {}
        for metric in _autolog_metric_allowlist:
            try:
                if hasattr(model, metric):
                    metric_value = getattr(model, metric)
                    if has_numpy:
                        # handle numpy floats
                        converted_metric = _convert_metric(metric_value)
                    else:
                        # simple conversion
                        converted_metric = None if math.isnan(float(metric_value)) else round(float(metric_value), 4)

                    if converted_metric:
                        result_metrics[metric] = _convert_metric(metric_value)
            except Exception:
                pass
        return result_metrics

    def _get_pyspark_ml_summary_metrics(self, summary: Any, prefix: str | None = None) -> dict[str, Any]:
        # metrics
        summary_metrics = {}
        for attr_name in dir(summary):
            # Skip special methods
            if not attr_name.startswith("__"):
                attr_value = getattr(summary, attr_name)
                # get simple values for now, there are pd.DF returns aswell
                if isinstance(attr_value, (float, int)):
                    if prefix:
                        summary_metrics[f"{prefix}_{attr_name}"] = attr_value
                    else:
                        summary_metrics[attr_name] = attr_value
        return summary_metrics
