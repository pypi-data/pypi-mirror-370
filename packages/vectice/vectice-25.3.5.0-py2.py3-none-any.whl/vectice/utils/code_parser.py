from __future__ import annotations

import ast
import os
import re
from collections import OrderedDict
from typing import Any

from IPython.core.inputtransformer2 import TransformerManager


# to view the node structure use ast.dump(node, indent=2)
class FilePathVisitor(ast.NodeVisitor):
    def __init__(self, is_graph_path: bool = False, is_dataset_path: bool = False):
        self.file_paths = set()
        self.dataset_file_paths = []
        self.is_graph_path = is_graph_path
        self.is_dataset_path = is_dataset_path

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name) or isinstance(node.func, ast.Attribute):
            # Record function args, kwargs.
            path_var_and_path = {"variable": None, "path": None}
            supported_path = False
            try:
                func_name = node.func.attr  # pyright: ignore[reportAttributeAccessIssue]
                if self.is_graph_path:
                    supported_path = self._is_supported_graph_library(func_name)
                if self.is_dataset_path:
                    supported_path = self._is_supported_dataset_library(func_name)
            except AttributeError:
                pass

            args = node.args + node.keywords
            for arg in args:
                arg_value = self._get_arg_or_kwarg_val(arg)
                if arg_value and self._is_valid_file(arg_value) and supported_path:
                    if self.is_dataset_path:
                        path_var_and_path["path"] = arg_value
                        self.dataset_file_paths.append(path_var_and_path)
                    if self.is_graph_path:
                        self.file_paths.add(arg_value)

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        path_var_and_path = {"variable": None, "path": None}

        try:
            if len(node.targets) == 1 and isinstance(
                node.targets[0], ast.Name
            ):  # pyright: ignore[reportAttributeAccessIssue]
                var_name = node.targets[0].id
                path_var_and_path["variable"] = var_name  # pyright: ignore[reportArgumentType]
                if isinstance(node.value, ast.Str):  # pyright: ignore[reportDeprecated]
                    path = node.value.s  # pyright: ignore[reportAttributeAccessIssue]
                    if self._is_valid_file(path):
                        if self.is_dataset_path:
                            path_var_and_path["path"] = path  # pyright: ignore[reportArgumentType]
                            self.dataset_file_paths.append(path_var_and_path)
                        if self.is_graph_path:
                            self.file_paths.add(path)
        except Exception:
            pass
        self.generic_visit(node)

    def _get_arg_or_kwarg_val(self, arg: Any) -> Any | None:
        try:
            # arg value
            if isinstance(arg.id, str):
                return arg.id  # pyright: ignore[reportAttributeAccessIssue]
        except AttributeError:
            pass
        try:
            # kwarg value if not a variable
            if isinstance(arg.value.value, str):
                return arg.value.value  # pyright: ignore[reportAttributeAccessIssue]
        except AttributeError:
            pass
        try:
            # kwarg value if it is a variable
            if isinstance(arg.value.id, str):
                return arg.value.id  # pyright: ignore[reportAttributeAccessIssue]
        except AttributeError:
            pass
        try:
            if isinstance(arg.value, str):
                return arg.value  # pyright: ignore[reportAttributeAccessIssue]
        except AttributeError:
            pass
        return None

    def _is_valid_file(self, path: str) -> bool:
        is_file = os.path.isfile(path)
        _, extension = os.path.splitext(path)
        if is_file or extension:
            return True
        return False

    def _is_supported_graph_library(self, func_name: str) -> bool:
        vectice_supported_graphs = [
            "savefig",
            "write_image",
        ]
        if func_name in vectice_supported_graphs:
            return True
        return False

    def _is_supported_dataset_library(self, func_name: str) -> bool:
        vectice_supported_datasets = [
            "read_csv",
        ]
        if func_name in vectice_supported_datasets:
            return True
        return False


class VariableVisitor(ast.NodeVisitor):
    def __init__(self, model_metrics: bool = False, custom_metrics: set[str | None] = set()):
        self.variables: OrderedDict[str, None] = OrderedDict()
        self.processed_variables: set[str] = set()
        self.function_call_args: set[str] = set()
        self.function_call_kwargs: set[str] = set()
        self.variable_calls: set[str] = set()
        self.vectice_call_vars: set[str] = set()
        self.metric_variables: set[str] = set()
        self.model_metrics = model_metrics
        self.custom_model_metrics: set[str | None] = custom_metrics

    ##### Implement NodeVisitor methods

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        for target in node.targets:
            self._extract_variables_from_target(target)
        self.generic_visit(node)
        if self.model_metrics:
            self._extract_metric_vars(node)

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802
        var_name = node.id
        # get functions args and kwargs
        args_kwargs = self.function_call_args.union(self.function_call_kwargs)
        all_processed_vars = self.processed_variables.union(self.variable_calls)
        if var_name not in all_processed_vars and var_name not in args_kwargs:
            self.variables[var_name] = None
            self.processed_variables.add(var_name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name) or isinstance(node.func, ast.Attribute):
            # Get variables that call functions
            if isinstance(node.func, ast.Attribute):
                try:
                    # Calls will fail
                    self.variable_calls.add(node.func.value.id)  # pyright: ignore[reportAttributeAccessIssue]
                except AttributeError:
                    pass
            # Record function args, kwargs.
            args = node.args + node.keywords
            for arg in args:
                arg_value = self._get_arg_or_kwarg_val(arg)
                if arg_value:
                    if hasattr(arg_value, "__iter__") and not isinstance(arg_value, str):
                        self.function_call_args = self.function_call_args.union(arg_value)
                    else:
                        self.function_call_args.add(arg_value)  # pyright: ignore[reportAttributeAccessIssue]

                func_name = self._get_function_name(node)
                if (
                    self._is_vectice_call_vars(func_name) or self._is_sklearn_search_call_vars(func_name)
                ) and arg_value:  # pyright: ignore[reportAttributeAccessIssue]
                    if hasattr(arg_value, "__iter__") and not isinstance(arg_value, str):
                        self.vectice_call_vars = self.vectice_call_vars.union(arg_value)
                    else:
                        self.vectice_call_vars.add(arg_value)
        self.generic_visit(node)

    def _get_function_name(self, node: ast.Call) -> str | None:
        try:
            if hasattr(node.func, "id"):
                return node.func.id  # pyright: ignore[reportAttributeAccessIssue]
            if hasattr(node.func, "value"):
                return node.func.value.id  # pyright: ignore[reportAttributeAccessIssue]
        except AttributeError:
            pass
        return None

    ##### VariableVisitor methods

    def _extract_variables_from_target(self, target: ast.expr) -> None:
        if isinstance(target, ast.Constant):
            return
        if isinstance(target, ast.Name):
            self.visit_Name(target)
        elif isinstance(target, ast.Tuple):
            for element in target.elts:
                if isinstance(element, ast.Name):
                    self.visit_Name(element)

    def _add_metric_variables(self, metric_variable: str, node: ast.Assign) -> None:
        try:
            # Get the function name
            function_call_name = node.value.func.id  # pyright: ignore[reportAttributeAccessIssue]
        except Exception:
            function_call_name = None

        try:
            # Get the function attr, e.g. BinaryClassificationEvaluator.evaluate() so evaluate is the attr
            function_attr = node.value.func.attr  # pyright: ignore[reportAttributeAccessIssue]
        except Exception:
            function_attr = None

        is_function_metric_call = self._is_metric_call_vars(function_call_name) if function_call_name else False
        is_method_metric_call = self._is_metric_call_vars(function_attr) if function_attr else False

        if is_function_metric_call or is_method_metric_call:
            self.metric_variables.add(metric_variable)

    def _extract_metric_vars(self, node: ast.Assign) -> None:
        # Get the variable
        for target in node.targets:
            metric_variable = None
            if isinstance(target, ast.Name):
                metric_variable = target.id
            if metric_variable:
                self._add_metric_variables(metric_variable, node)

    def _get_arg_or_kwarg_val(self, arg: Any) -> Any | None:
        try:
            # remove potential of pyspark arg == metric name e.g RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
            if arg.arg == "metricName":
                return None
        except AttributeError:
            pass
        try:
            # arg value
            return arg.id
        except AttributeError:
            pass
        try:
            # kwarg value if not a variable
            return arg.value.value
        except AttributeError:
            pass
        try:
            # kwarg value if it is a variable
            return arg.value.id
        except AttributeError:
            pass
        try:
            # kwarg value if it is a list, list can contain multiple var types so we recursilvely get the arg/kwarg
            return {self._get_arg_or_kwarg_val(arg_value) for arg_value in arg.value.elts}
        except AttributeError:
            pass
        return None

    def _is_vectice_call_vars(self, func_name: str | None) -> bool:
        if not func_name:
            return False
        vectice_functions = [
            "NoResource",
            "Resource",
            "Table",
            "SnowflakeResource",
            "FileResource",
            "GCSResource",
            "S3Resource",
            "BigQueryResource",
            "DatabricksTableResource",
            "Dataset",
            "Model",
        ]
        if func_name in vectice_functions:
            return True
        return False

    def _is_sklearn_search_call_vars(self, func_name: str | None) -> bool:
        """Filter our sklearn search args & kwargs"""
        try:
            from sklearn.model_selection import _search  # pyright: ignore[reportPrivateUsage]
        except ImportError:
            return False

        if not func_name:
            return False
        sklearn_search_calls = dir(_search)
        return func_name in sklearn_search_calls

    def _is_metric_call_vars(self, func_name: str) -> bool:
        all_metrics = []
        sklearn_metrics = _get_sklearn_metrics()

        h2o_metrics = _get_h2o_metrics()

        all_metrics.extend(sklearn_metrics)
        all_metrics.extend(h2o_metrics)
        # Pyspark e.g BinaryClassificationEvaluator.evaluate()
        all_metrics.extend(["evaluate"])
        ## TODO: clean
        if self.custom_model_metrics:
            all_metrics += list(self.custom_model_metrics)

        if func_name in all_metrics:
            return True
        return False


def parse_comments(code: str) -> list[dict]:
    # Get all comments and variables
    comments_and_variables = r"##\s*(.*?)(?:$|\n)|(.+?)\s*=\s*.*?(?:$|\n)"
    all_comments_and_variables = []
    for idx, match in enumerate(re.findall(comments_and_variables, code)):
        comment, variable = match
        # Create placeholder for no variable found
        variable = variable if variable else f"variable_{idx}"
        # Remove empty string matches
        comment = comment if comment else None
        all_comments_and_variables.append({"variable": variable, "comment": comment})
    return all_comments_and_variables


def preprocess_code(code: str) -> str:
    # Ipython transform manager to make code ast parsable and python executable
    transform_manager = TransformerManager()
    transform_cell = transform_manager.transform_cell(code)
    complete = transform_manager.check_complete(transform_cell)
    # returns ('complete', None) or ('invalid', None)
    if complete[0] == "complete":
        return transform_cell
    return ""


def _get_sklearn_metrics() -> list[str]:
    """Get sklearn model metrics."""
    try:
        from sklearn.metrics import (
            _classification,  # pyright: ignore[reportPrivateUsage]
            _ranking,  # pyright: ignore[reportPrivateUsage]
            _regression,  # pyright: ignore[reportPrivateUsage]
            _scorer,  # pyright: ignore[reportPrivateUsage]
            cluster,  # pyright: ignore[reportPrivateUsage]
        )

        return dir(_classification) + dir(_ranking) + dir(_regression) + dir(_scorer) + dir(cluster)
    except ImportError:
        return []


def _get_h2o_metrics() -> list[str]:
    """Get H2O model metrics."""
    try:
        from h2o.model.metrics import (  # pyright: ignore[reportMissingImports]
            H2OAnomalyDetectionModelMetrics,  # pyright: ignore[reportMissingImports]
            H2OBinomialModelMetrics,  # pyright: ignore[reportMissingImports]
            H2OBinomialUpliftModelMetrics,  # pyright: ignore[reportMissingImports]
            H2OClusteringModelMetrics,  # pyright: ignore[reportMissingImports]
            H2ODefaultModelMetrics,  # pyright: ignore[reportMissingImports]
            H2ODimReductionModelMetrics,  # pyright: ignore[reportMissingImports]
            H2OMultinomialModelMetrics,  # pyright: ignore[reportMissingImports]
            H2OOrdinalModelMetrics,  # pyright: ignore[reportMissingImports]
            H2ORegressionCoxPHModelMetrics,  # pyright: ignore[reportMissingImports]
            H2ORegressionModelMetrics,  # pyright: ignore[reportMissingImports]
        )

        return (
            dir(H2OAnomalyDetectionModelMetrics)
            + dir(H2OBinomialModelMetrics)
            + dir(H2OClusteringModelMetrics)
            + dir(H2ORegressionCoxPHModelMetrics)
            + dir(H2ODimReductionModelMetrics)
            + dir(H2ODefaultModelMetrics)
            + dir(H2OMultinomialModelMetrics)
            + dir(H2OOrdinalModelMetrics)
            + dir(H2ORegressionModelMetrics)
            + dir(H2OBinomialUpliftModelMetrics)
        )
    except ImportError:
        return []
