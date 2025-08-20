from __future__ import annotations

import ast
import logging
import re
import uuid
from collections import OrderedDict
from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import matplotlib.pyplot as plt
from typing_extensions import TypedDict

from vectice.api.http_error_handlers import VecticeException
from vectice.autolog.asset_services.service_types import GiskardType, ModevaType, VecticeType
from vectice.autolog.autolog_asset_factory import AssetFactory
from vectice.models.dataset import Dataset
from vectice.models.model import Model
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_representation import ModelRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation
from vectice.models.table import Table
from vectice.models.validation import ValidationModel
from vectice.utils.code_parser import VariableVisitor, parse_comments, preprocess_code
from vectice.utils.common_utils import ensure_correct_project_id_from_representation_objs
from vectice.utils.last_assets import _get_asset_parent_name  # pyright: ignore [reportPrivateUsage]

if TYPE_CHECKING:
    from modeva.utils.results import ValidationResult  # type: ignore[reportMissingImports]
    from pandas import DataFrame
    from pyspark.sql import DataFrame as SparkDF
    from sklearn.pipeline import Pipeline

    # Vectice Object types
    from vectice.autolog.asset_services import TVecticeObjects
    from vectice.models import Phase
    from vectice.models.resource.metadata.db_metadata import TableType

    # container for metric tables and future floating assets
    TMetric = TypedDict(
        "TMetric",
        {
            "variable": str,
            "tables": list[Table | None],
            "asset_type": VecticeType,
        },
    )

    TModel = TypedDict(
        "TModel",
        {
            "variable": str,
            "model": Model,
            "summary": str,
            "asset_type": VecticeType,
        },
    )

    DataframeTypes = TypeVar("DataframeTypes", SparkDF, DataFrame)
    TDataset = TypedDict(
        "TDataset",
        {
            "variable": str,
            "dataset": Dataset,
            "asset_type": VecticeType,
        },
    )
    TValidationResult = TypedDict(
        "TValidationResult",
        {"variable": str, "table": DataframeTypes, "plot": TableType, "asset": ValidationResult},
    )
    TFactSheet = TypedDict(
        "TFactSheet",
        {"dataset": DataframeTypes, "models": list, "validation_results": list[TValidationResult]},
    )

    TWidgetOutput = TypedDict(
        "TWidgetOutput",
        {
            "variable": str,
            "output": Any,
            "asset_type": VecticeType,
        },
    )


try:
    from IPython.core.getipython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "To use autolog, please install extra dependencies from vectice package using '%pip install vectice[autolog]'"
    ) from None

is_plotly = False
is_matplotlib = False
if find_spec("plotly") is not None:
    is_plotly = True

if find_spec("matplotlib") is not None:
    is_matplotlib = True

_logger = logging.getLogger(__name__)

NOTEBOOK_CELLS = {}
GRAPHS = {}
IPYTHON_SESSION = None


def validate_ipython_session(ipython: Any) -> bool:
    """Validate IPython session. As opening and closing the browser will create a new header and session. The cellIds become untrackable."""
    global IPYTHON_SESSION
    global GRAPHS

    ipython_session_id = ipython.get_parent()["header"]["session"]  # type: ignore
    if IPYTHON_SESSION and IPYTHON_SESSION != ipython_session_id:
        GRAPHS = {}  # pyright: ignore[reportConstantRedefinition]
        IPYTHON_SESSION = ipython_session_id  # pyright: ignore[reportConstantRedefinition]
        return False

    IPYTHON_SESSION = ipython_session_id  # pyright: ignore[reportConstantRedefinition]
    return True


# TODO - migrate to our vectice id for all notebooks
def _inject_vectice_cell_id(ipython: Any) -> str:
    """Injects a cell id into the IPython metadata."""
    ipython_metadata = ipython.get_parent()  # type: ignore
    if ipython_metadata.get("metadata", {}).get("vecticeId", False):  # type: ignore
        return ipython_metadata["metadata"]["vecticeId"]  # type: ignore
    vectice_id = str(uuid.uuid4())
    # Inject the vecticeId into the metadata
    ipython.get_parent()["metadata"]["vecticeId"] = vectice_id  # type: ignore
    return vectice_id


def _get_cell_id(ipython: Any):
    try:
        ipython_metadata = ipython.get_parent()  # type: ignore
        cell_metadata = ipython_metadata.get("metadata", {})  # type: ignore
        _logger.debug(f"Cell Metadata {cell_metadata}")
        if cell_metadata.get("colab") and "cell_id" in cell_metadata.get("colab"):  # type: ignore
            cell_id = cell_metadata["colab"]["cell_id"]
        elif cell_metadata.get("commandId"):  # type: ignore
            cell_id = cell_metadata["commandId"]
        elif ipython_metadata.get("cellId", False):  # type: ignore
            cell_id = ipython_metadata["cellId"]
        else:
            # if no cellId is found, inject a new one. Persists in Ipython metadata
            _logger.debug("No cellId found in metadata, injecting a new VecticeId.")
            cell_id = _inject_vectice_cell_id(ipython)  # type: ignore
        return cell_id
    except Exception as e:
        _logger.debug(f"Unable to retrieve CellId.\n{e}")
    return None


def start_listen() -> Any:
    ipython = get_ipython()  # type: ignore

    def _notebook_cell_content_update():
        global NOTEBOOK_CELLS

        cell_id = _get_cell_id(ipython)
        try:
            cell_content = ipython.get_parent()["content"]["code"]  # type: ignore
            NOTEBOOK_CELLS[cell_id] = cell_content
        except Exception as e:
            _logger.debug(f"Notebook cell content failed to update.\n{e}")

    def _setup_cell():
        # if a cell is run or re-run, clear the dictionary
        cell_id = _get_cell_id(ipython)
        if cell_id:
            GRAPHS[cell_id] = {
                "saved": [],
                "displayed": [],
            }

    def _load_ipython_extension():
        is_inline = True
        try:
            from matplotlib_inline.backend_inline import flush_figures
        except ImportError:
            is_inline = False

        from vectice.utils.plot_tracker import PlotTracker

        # Connect the plot tracker hook to IPython's display hook
        # NB we monkey patch plotly if package is found, see in plot_tracker.py
        plot_tracker = PlotTracker(is_inline)
        # Apply the patch for savefig
        plt.savefig = plot_tracker.patched_savefig

        # unregister the matplotlib inline event
        # this is done so the graphs aren't flushed before we can capture them
        is_flush_figure_registered = get_event_callback(ipython, "post_execute", "flush_figures")
        if is_flush_figure_registered:
            ipython.events.unregister("post_execute", flush_figures)  # type: ignore

        """Load the extension in IPython."""
        ipython.events.register("pre_execute", _setup_cell)  # type: ignore
        ipython.events.register("post_execute", _notebook_cell_content_update)  # type: ignore
        ipython.events.register("post_execute", plot_tracker.get_all_figures)  # type: ignore
        # register the matplotlib event so we don't break the display output
        if is_flush_figure_registered:
            ipython.events.register("post_execute", flush_figures)  # type: ignore

    pre_execute_callback = get_event_callback(ipython, "pre_execute", "_setup_cell")
    post_execute_callback = get_event_callback(ipython, "post_execute", "_notebook_cell_content_update")
    post_run_cell_callback = get_event_callback(ipython, "post_execute", "get_all_figures")
    if ipython and not (pre_execute_callback and post_execute_callback and post_run_cell_callback):  # type: ignore
        _load_ipython_extension()

    return ipython


def get_event_callback(ipython: InteractiveShell | None, event_name: str, callback_name: str) -> Callable | None:
    """Helper function to find a registered callback by name."""
    if ipython:
        event_callbacks = [ev for ev in ipython.events.callbacks[event_name] if callback_name in str(ev)]
        return event_callbacks[0] if event_callbacks else None
    return None


####### Autolog logic
class Autolog:
    def __init__(
        self,
        phase: Phase | None,
        ipy: InteractiveShell,
        is_notebook: bool,
        create: bool = True,
        note: str | None = None,
        capture_schema_only: bool = True,
        capture_comments: bool = True,
        prefix: str | None = None,
        capture_widget_graphs: bool = False,
        organize_with_ai: bool = False,
        generate_report: bool = False,
    ):
        from vectice.services.phase_service import PhaseService

        if phase is None:
            raise ValueError("Login")

        if create is True:
            iteration = phase.create_iteration()
        else:
            iteration = PhaseService(
                phase._client  # pyright: ignore[reportPrivateUsage]
            ).get_active_iteration_or_create(phase)

        self._iteration = iteration
        self._iteration_service = iteration._service  # pyright: ignore[reportPrivateUsage]
        self._capture_schema_only = capture_schema_only
        self._ip = ipy
        self._local_vars = self._ip.user_global_ns
        self._metric_functions = self._get_metric_functions()
        self._capture_comments = capture_comments
        self._prefix = prefix
        self._is_notebook = is_notebook
        self._cell_content = self._get_notebook_cell_content() if is_notebook is True else self._get_cell_content()
        self._vectice_data = self._get_variable_matches(self._local_vars)
        self._failed_assets = []

        # Get back objects to log
        self._assets = self._get_assets()
        graphs = self._get_graphs(is_notebook, capture_widget_graphs)

        if note:
            self._iteration_service.log_comment(note)
            _logger.info(f"Note logged in iteration {self._iteration.name!r}.")

        # Log objects

        self._log_assets(self._assets)

        if graphs:
            for graph in graphs:
                try:
                    self._iteration_service.log_image_or_file(graph)
                    graph = graph if isinstance(graph, str) else graph.filename
                    _logger.info(f"Graph {graph!r} logged in iteration {self._iteration.name!r}.")
                except Exception as e:
                    self._failed_assets.append({"reason": e, "asset": graph, "type": "Graph"})

        if len(self._failed_assets):
            _logger.warning("The following assets failed to log:")
        for failed_asset in self._failed_assets:
            _logger.warning(f"{failed_asset['type']} {failed_asset['asset']!r}, reason: {failed_asset['reason']}")
        # clear metrics - prevents non capture
        self._clear_metric_assets()

        cells = [{"cellId": key, "content": value} for key, value in NOTEBOOK_CELLS.items()]
        self._iteration_service.save_autolog_assets(
            list(filter(lambda cell: cell["cellId"] is not None, cells)),  # type: ignore
            prefix,
        )
        if organize_with_ai:
            if generate_report:
                self._iteration_service.organize_with_ai_and_report()
            else:
                self._iteration_service.organize_with_ai()

        # notebook_path = get_notebook_path()
        # if save_notebook and notebook_path:
        #     self._iteration._log_image_or_file(notebook_path, section="Notebook")  # type: ignore[reportPrivateUsage]

    def _get_metric_functions(self) -> set[str | None]:
        safe_keys = set()
        SparkDataFrame = None

        try:
            from pyspark.sql import DataFrame as PySparkDataFrame

            SparkDataFrame = PySparkDataFrame
        except ImportError:
            pass  # Spark not available

        for name, func in self._local_vars.items():
            try:
                if SparkDataFrame and isinstance(func, SparkDataFrame):
                    continue
                if getattr(func, "custom_metric_function", False):
                    safe_keys.add(name)
            except Exception as e:
                _logger.debug(f"Skipping variable '{name}' during metric function check: {e}")
                continue

        return safe_keys

    def _get_variable_matches(self, local_vars: dict[str, Any]) -> list[dict[Any, Any]]:
        vectice_data = []
        all_cell_vars = set()
        all_vectice_calls = set()
        for cell_not_processed in self._cell_content:
            cell = preprocess_code(cell_not_processed)
            variable_comments = parse_comments(cell_not_processed) if self._capture_comments else []
            vectice_match = {}
            all_vars: OrderedDict[str, Any] = OrderedDict()

            vectice_match["cell"] = cell
            vectice_match["comments"] = variable_comments

            # Parse the cell content using the VariableVisitor
            try:
                tree = ast.parse(cell)
            except SyntaxError as err:
                raise SyntaxError(
                    "Autolog is unable to parse the code. Make sure all non-Python syntax, such as bash commands, are properly indented and preceded by '%' or '!'. If the error persist, please contact your sales representative."
                ) from err

            visitor = VariableVisitor(custom_metrics=self._metric_functions)
            visitor.visit(tree)
            # Keep set of all vectice call vars
            all_vectice_calls = all_vectice_calls.union(visitor.vectice_call_vars)
            # Update all_vars with variable names and values in the order they appear
            for var in visitor.variables:
                if var in local_vars and var not in all_vars:
                    all_vars[var] = local_vars[var]
                # check if the var exists in a previous cell for autolog.notebook before the vectice object uses the var
                if self._is_notebook:
                    all_vectice_calls = {vect_var for vect_var in all_vectice_calls if vect_var not in all_cell_vars}
                # Keep track of all vars
                all_cell_vars.add(var)

            vectice_match["variables"] = all_vars
            vectice_data.append(vectice_match)
        clean_vectice_data = []
        for data in vectice_data:
            for var in all_vectice_calls:
                # the order of cells misses vars
                if var in data["variables"]:
                    del data["variables"][var]
            # check that there are vars for the cell and then append or if there are comments
            if len(data["variables"]) >= 1 or len(data["comments"]) >= 1:
                clean_vectice_data.append(data)
        return clean_vectice_data

    def _get_notebook_cell_content(self) -> list[Any]:
        try:
            cell_id = _get_cell_id(self._ip)
            cell_content = self._ip.get_parent()["content"]["code"]  # type: ignore
            NOTEBOOK_CELLS[cell_id] = cell_content
        except Exception as e:
            _logger.debug(f"Failed to get notebook cell content.\n{e}")
        return list(NOTEBOOK_CELLS.values())

    def _get_cell_content(self) -> list[Any]:
        """Used by autolog cell to get the content of the cell. This is used to parse for variables."""
        cell_content = self._ip.get_parent()["content"]["code"]  # pyright: ignore[reportAttributeAccessIssue]
        if cell_content is None:
            raise ValueError("Failed to get cell content.")
        return [cell_content]

    def _get_asset_comments(self, comments: dict, key: str) -> tuple[str | None, str | None]:
        try:
            comment_before = comments["comment_matches_before"][key]["comment"]
        except KeyError:
            comment_before = None
        try:
            comment_after = comments["comment_matches_after"][key]["comment"]
        except KeyError:
            comment_after = None
        return comment_before, comment_after

    def _get_assets(self) -> list[TModel | TDataset | TVecticeObjects | TWidgetOutput]:
        """Collects assets by processing vectice data and deduplicates them."""
        assets = []
        phase_name = self._iteration.phase.id
        processed_keys = set()

        for data in self._vectice_data:
            # Process variables
            for key, asset in data["variables"].items():
                if not key.startswith("_") and key not in processed_keys:  # Skip cell inputs/outputs
                    self._process_variable(key, asset, data, phase_name, assets)
                    processed_keys.add(key)

            # Process metrics
            self._process_metric(data, assets)

        return self._deduplicate_assets(assets)

    def _process_variable(self, key: str, asset: Any, data: dict, phase_name: str, assets: list[dict[str, Any]]):
        """Processes a single variable and adds its asset to the list if valid."""
        try:
            asset_service = AssetFactory.get_asset_service(
                key,
                asset,
                data,
                phase_name,
                self._metric_functions,
                self._cell_content,
                self._capture_schema_only,
                self._prefix,
            )
            asset_information = asset_service.get_asset()
            if asset_information:
                assets.append(asset_information)
        except VecticeException:
            pass

    def _process_metric(self, data: dict, assets: list[dict[str, Any]]):
        from vectice.autolog.asset_services.metric_service import MetricService

        try:
            metric_asset = MetricService(data, self._metric_functions).get_assets()
            if metric_asset:
                assets.append(metric_asset)
        except VecticeException:
            pass

    def _deduplicate_assets(
        self, assets: list[dict[str, Any]]
    ) -> list[TModel | TDataset | TVecticeObjects | TWidgetOutput]:
        unique_dict = {}
        result = []

        for item in assets:
            variable = item["variable"]

            if variable not in unique_dict.keys():
                # If variable is not seen before, add it to the dictionary
                unique_dict[variable] = item
                result.append(item)
            else:
                existing_item = unique_dict[variable]
                if "vectice_object" in item:
                    existing_item["vectice_object"] = item["vectice_object"]
                elif "dataframe" in item:
                    existing_item["type"] = item["type"]
                elif "library" in item:
                    existing_item["library"] = item["library"]

                    # Merge dictionaries for the "metrics" attribute
                    existing_item_metrics = existing_item["metrics"]
                    item_metrics = item["metrics"]

                    for key, value in item_metrics.items():
                        existing_item_metrics[key] = value
                elif "validation_results" in item:
                    existing_item["dataset"] = item["dataset"]
                    existing_item["models"] = item["models"]
                    existing_item["validation_results"] = item["validation_results"]
                elif "table" in item:
                    existing_item["table"] = item["table"]
                    existing_item["plot"] = item["plot"]
                elif "tables" in item:
                    existing_item["tables"] = item["tables"]
        return result

    def _clear_metric_assets(self):
        # clear metric assets after autolog
        from vectice.autolog.asset_services.metric_service import captured_metrics

        captured_metrics.clear()

    def _get_pipeline_steps(self, pipeline: Pipeline) -> dict:
        sklearn_pipeline = {}
        try:
            for step in pipeline.steps:
                step_name, step_obj = step
                if hasattr(step_obj, "named_transformers_"):
                    for k, v in step_obj.named_transformers_.items():
                        sklearn_pipeline[f"pipeline_{step_name}_{k}_steps"] = list(v.named_steps.keys())
            return sklearn_pipeline
        except Exception:
            return sklearn_pipeline

    def _get_pipeline_info(self, pipeline: Pipeline) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        # if pipeline with classifier
        try:
            from sklearn.base import is_classifier, is_regressor

            model = pipeline.steps[-1][-1]
            model_name = pipeline.steps[-1][0]
            if is_regressor(model) or is_classifier(model):
                model_params = {
                    f"{model_name}_{key}": value
                    for key, value in model.get_params().items()
                    if value is not None and bool(str(value))
                }
                model_params.update(self._get_pipeline_steps(pipeline))
                return "sklearn-pipeline", model_params
        except Exception:
            pass

        try:
            pipeline_params = {
                str(key): value
                for key, value in pipeline.get_params().items()
                if value is not None and bool(str(value))
            }
            return "sklearn-pipeline", pipeline_params
        except Exception:
            return None, None

    def _get_all_cells_comments(self) -> list[dict]:
        # Get all comments from all cells
        all_comments_and_variables = []
        for data in self._vectice_data:
            if data["comments"]:
                for comments in data["comments"]:
                    all_comments_and_variables.append(comments)
        return all_comments_and_variables

    def _get_comments_before(
        self,
        all_comments_and_variables: list[dict],
        asset: TModel | TDataset | TVecticeObjects | TWidgetOutput,
        comments_logged: list,
    ):
        comments_to_log = []
        for data in all_comments_and_variables:
            # If we find the variable we log all the comments found
            if data["variable"] == asset["variable"]:
                return comments_to_log
            # We only want comments remaining
            if data["comment"] not in comments_logged:
                comments_to_log.append(data["comment"])
        # return nothing if we don't see the asset
        return []

    def _log_comments_before_asset(
        self,
        all_comments_and_variables: list[dict],
        asset: TModel | TDataset | TVecticeObjects | TWidgetOutput,
        comments_logged: list,
    ) -> list:
        # Get comments to log before each asset
        comments_before = self._get_comments_before(all_comments_and_variables, asset, comments_logged)
        # Log comments before each asset
        if comments_before:
            for comment in comments_before:
                if comment:
                    self._iteration_service.log_comment(comment)
            # Keep track of what's logged
            return comments_logged + comments_before
        return comments_logged

    def _log_remaining_comments(self, all_unique_comments: set, comments_logged: list) -> None:
        # Ensure last asset comments are filtered out
        all_comments_logged = set(comments_logged)
        still_comments_to_log = list(all_unique_comments - all_comments_logged)
        # Log remaining comments after last asset
        if still_comments_to_log:
            for comment in still_comments_to_log:
                if comment:
                    self._iteration_service.log_comment(comment)
        # Logging for comments captured
        all_comments_logged.discard(None)
        filtered_comments = list(filter(lambda comment: comment is not None, still_comments_to_log))
        if filtered_comments or all_comments_logged:
            _logger.info(f"Comments logged in iteration {self._iteration.name!r}.")

    def _log_modeva_asset(self, asset: TModel | TDataset | TVecticeObjects | TWidgetOutput):
        try:
            # if asset and (asset.get("models") or "dataframe" in asset):
            # self._iteration._log_fact_sheet(asset)  # type: ignore[reportPrivateUsage]
            if asset and "table" in asset:
                self._iteration._log_validation_result(asset)  # type: ignore[reportPrivateUsage]
        except Exception:
            pass

    def _log_asset_types(
        self,
        asset: TModel | TDataset | TVecticeObjects | TWidgetOutput,
        asset_type: VecticeType | GiskardType | ModevaType,
    ) -> None:
        if asset_type == VecticeType.VECTICE_OBJECT:
            self._log_vectice_asset(asset)  # type: ignore[reportArgumentType]
        elif asset_type == VecticeType.MODEL:
            self._log_model(asset)  # type: ignore[reportArgumentType]
        elif asset_type == VecticeType.DATASET:
            self._log_dataset(asset)  # type: ignore[reportArgumentType]
        elif asset_type == VecticeType.METRIC:
            self._log_metric_asset(asset)  # type: ignore[reportArgumentType]
        elif asset_type == GiskardType.RAG:
            self._iteration._log_rag_report(asset)  # type: ignore[reportPrivateUsage]
        elif asset_type == GiskardType.SCAN:
            self._iteration._log_scan_report(asset)  # type: ignore[reportPrivateUsage]
        elif asset_type == GiskardType.QATESTSET:
            self._iteration._log_qa_test(asset)  # type: ignore[reportPrivateUsage]
        elif asset_type == GiskardType.TEST_SUITE_RESULT:
            self._iteration._log_test_suite_result(asset)  # type: ignore[reportPrivateUsage]
        elif asset_type == ModevaType.VALIDATION_RESULT:
            self._log_modeva_asset(asset)

    def _log_assets(
        self,
        assets: list[TModel | TDataset | TVecticeObjects | TWidgetOutput],
    ):
        from vectice.services import iteration_service

        # all comments and variables
        all_comments_and_variables = self._get_all_cells_comments()
        # Unique comment set
        all_unique_comments = set([data["comment"] for data in all_comments_and_variables])
        # Keep track of what is logged
        comments_logged = []
        for asset in assets:
            asset_type = asset["asset_type"]
            try:
                comments_logged = self._log_comments_before_asset(all_comments_and_variables, asset, comments_logged)
                self._log_asset_types(asset, asset_type)
            except Exception as e:
                self._failed_assets.append({"reason": e, "asset": asset["variable"], "type": asset_type.value})
        # Log the remaining comments
        self._log_remaining_comments(all_unique_comments, comments_logged)
        # After logging, don't re-use code file
        iteration_service.lineage_file_id = None

    def _log_model(self, model: TModel):
        vectice_model = model["model"]
        self._iteration_service.log_model(vectice_model)
        _logger.info(f"Model {vectice_model.name!r} logged in iteration {self._iteration.name!r}.")
        model_summary = model.get("summary")

        if model_summary:
            # log statsmodel summary
            self._iteration_service.log_comment(model_summary)

    def _log_metric_asset(self, metric: TMetric):
        metric_tables = metric.get("tables")
        for table in metric_tables:
            if table is not None:
                self._iteration_service.log_table(table)
                _logger.info(f"Table {table.name!r} logged in iteration {self._iteration.name!r}.")

    def _log_vectice_asset(self, asset: TVecticeObjects) -> None:
        asset_to_log = asset["vectice_object"]
        if isinstance(asset_to_log, ValidationModel):
            object_name = asset["variable"]
        else:
            object_name = asset_to_log.name

        ensure_correct_project_id_from_representation_objs(self._iteration.project.id, asset_to_log)

        if isinstance(asset_to_log, Dataset):
            self._iteration_service.log_dataset(asset_to_log)
            _logger.info(f"Dataset {object_name!r} logged in iteration {self._iteration.name!r}.")
        elif isinstance(asset_to_log, Table):
            self._iteration_service.log_table(asset_to_log)
            _logger.info(f"Table {object_name!r} logged in iteration {self._iteration.index!r}.")
        elif isinstance(asset_to_log, Model):
            if asset_to_log.predictor:
                self._iteration._assign_model_predictor_metadata(asset_to_log)  # pyright: ignore[reportPrivateUsage]
            self._iteration_service.log_model(asset_to_log)
            _logger.info(f"Model {object_name!r} logged in iteration {self._iteration.index!r}.")
        elif isinstance(
            asset_to_log,
            (ModelRepresentation, ModelVersionRepresentation, DatasetRepresentation, DatasetVersionRepresentation),
        ):
            asset_type, already_assigned = self._iteration_service.assign_version_representation(
                asset_to_log
            )  # pyright: ignore[reportPrivateUsage]
            link = "already linked" if already_assigned else "linked"
            asset_name_variable = asset["variable"]
            is_parent = isinstance(asset_to_log, (ModelRepresentation, DatasetRepresentation))
            asset_version = (
                asset_to_log._last_version.name  # pyright: ignore [reportPrivateUsage]
                if (is_parent and asset_to_log._last_version is not None)  # pyright: ignore [reportPrivateUsage]
                else asset_to_log.name
            )
            asset_name = (
                asset_to_log.name
                if is_parent
                else _get_asset_parent_name(asset_to_log)  # pyright: ignore [reportPrivateUsage]
            )
            _logger.info(
                f"{asset_type} {asset_name!r} {asset_version} named {asset_name_variable!r} as a variable {link} to iteration {self._iteration.index!r}."
            )
        else:
            self._iteration._log_validation_model(asset_to_log)  # pyright: ignore[reportPrivateUsage]

    def _log_dataset(self, dataset: TDataset) -> None:
        vec_dataset = dataset["dataset"]
        try:
            self._iteration_service.log_dataset(vec_dataset)
        except FileNotFoundError:
            self._iteration_service.log_dataset(vec_dataset)
        _logger.info(f"Dataset {vec_dataset.name!r} logged in iteration {self._iteration.name!r}.")

    def _get_graphs(self, is_notebook: bool, capture_widget_graphs: bool = False) -> list[Any]:
        global GRAPHS
        if capture_widget_graphs and self._get_widget_graphs():
            # update graphs with widget graphs
            self.extract_and_save_widget_graphs()
        graphs = []
        if is_notebook:
            displayed_graphs = [displayed_graph for cell in GRAPHS.values() for displayed_graph in cell["displayed"]]
            saved_graphs = {graph for cell in GRAPHS.values() for graph in cell["saved"]}
        else:
            cell_id = _get_cell_id(self._ip)
            cells_graphs = GRAPHS[cell_id]
            displayed_graphs = cells_graphs["displayed"]
            saved_graphs = set(cells_graphs["saved"])
        graphs += list(saved_graphs)
        graphs += displayed_graphs
        return graphs

    def _get_widget_graphs(self) -> bool:
        """NB Only supports plotly currently."""
        from importlib.metadata import version

        from packaging.version import Version

        is_ipywidgets, is_kaleido = False, False
        if find_spec("ipywidgets") is not None:
            is_ipywidgets = True

        if is_ipywidgets and find_spec("kaleido") is not None:
            is_kaleido = True
            kaleido_version = version("kaleido")
            if Version(kaleido_version) >= Version("0.2.0"):
                _logger.warning(
                    f"Kaleido {kaleido_version!r} has known issues with plotly write_image. Install 0.1.0 or 0.1.0post1 for a stable experience."
                )

        if is_plotly:
            plotly_version = version("plotly")
            if Version(plotly_version) >= Version("6.0.0"):
                _logger.warning(
                    f"Plotly {plotly_version!r} and greater has known issues with ipywidgets. Install an older version of plotly for a stable experience."
                )

        if not (is_plotly and is_ipywidgets and is_kaleido):
            return False
        return True

    def extract_and_save_widget_graphs(self):
        """Extracts and saves figures from all detected `ipywidgets.Output` widgets or from the autolog.cell `ipywidgets.Output`.

        We have plotly write_img monkey patched so implicitly we are capturing what we write as an image below.
        """
        import plotly.graph_objects as go

        # Will be the cells widget or all widgets
        output_widgets = [
            asset["output"]  # pyright: ignore[reportGeneralTypeIssues]
            for asset in self._assets  # pyright: ignore[reportGeneralTypeIssues]
            if asset["asset_type"] == VecticeType.IPYWIDGETS_OUTPUT  # pyright: ignore[reportGeneralTypeIssues]
        ]
        for widget in output_widgets:
            for figure_count, out in enumerate(widget.outputs):
                is_plotly_graph = (
                    isinstance(out, dict) and "data" in out and "application/vnd.plotly.v1+json" in out["data"]
                )
                if is_plotly_graph:
                    fig_dict = out["data"]["application/vnd.plotly.v1+json"]
                    fig = go.Figure(fig_dict)  # pyright: ignore[reportCallIssue]
                    # Generate a meaningful filename based on the plot title
                    plot_title = (
                        fig.layout.title.text  # pyright: ignore[reportAttributeAccessIssue]
                        if fig.layout.title.text  # pyright: ignore[reportAttributeAccessIssue]
                        else f"figure_{figure_count}"  # pyright: ignore[reportAttributeAccessIssue]
                    )
                    invalid_chars_pattern = r'[ ,<>:"/\\|?*]'
                    filename = f"{re.sub(invalid_chars_pattern, '_', plot_title)}.png"
                    # Save the figure and trigger monkey patch
                    fig.write_image(filename)
