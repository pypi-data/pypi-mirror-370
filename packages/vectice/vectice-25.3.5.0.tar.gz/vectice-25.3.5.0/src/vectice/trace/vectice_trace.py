from __future__ import annotations

import logging
import warnings

from vectice.api.http_error_handlers import VecticeException
from vectice.models.dataset import Dataset
from vectice.models.model import Model
from vectice.models.table import Table
from vectice.trace.code_trace_service import CodeTraceService
from vectice.trace.graph_patch_service import GraphPatchService
from vectice.trace.trace_client_service import TraceClientService
from vectice.utils.common_utils import get_asset_name

_logger = logging.getLogger(__name__)


class VecticeTrace(CodeTraceService):
    """VecticeTrace is a context manager that integrates Vectice's tracing capabilities with Python's code tracing.

    It captures the execution of Python code, including variables and function calls, and logs Vectice assets
    such as datasets, models, and tables to the current iteration in Vectice.

    ```python
    with VecticeTrace(
            phase = 'PHA-XXX'           # Paste your Phase Id)
        as trace:
        # Your code here
        dataset = Dataset(name="example_dataset")
    ```

    Environmental variables can be set for the trace configuration in a .env file.
    ```
    VECTICE_API_TOKEN='your-api-key'
    VECTICE_HOST='your-host-url'
    ```

    The environmental variables can also be set in the CLI.
    ```bash
    export VECTICE_API_TOKEN='your-api-key'
    export VECTICE_HOST='your-host-url'
    ```

    The environmental variables can also be set in directly.
    ```python
    import os
    os.environ['VECTICE_API_TOKEN'] = token
    os.environ['VECTICE_HOST'] = host
    ```

    Parameters:
        phase: The ID of the phase in which you wish to autolog your work as an iteration.
        prefix: A Prefix which will be applied to logged models and datasets variable name. e.g `my-prefix` will be `my-prefix-variable`,
            an empty string will be `variable` and no prefix will be `PHA-XXX-variable`.
        create_new_iteration: If set to False, logging of assets will happen in the last updated iteration. Otherwise, it will create a new iteration for logging the cell's assets.

    """

    def __init__(
        self,
        phase: str | None = None,
        prefix: str | None = None,
        create_new_iteration: bool = False,
    ):
        if self._is_ipython_environment():
            raise VecticeException(
                "Ipython environments are currently not supported by Vectice Trace. Please use Autolog instead."
                "For detailed information about autolog, supported libraries and environments please consult the documentation: https://api-docs.vectice.com/reference/vectice/autolog/"
            )
        CodeTraceService.__init__(self)
        self._client = TraceClientService(phase, create_new_iteration)
        self._graph_patch_service = GraphPatchService()
        self._failed_assets = []
        self._prefix = prefix

    def __enter__(self):
        """Enhanced context manager that coordinates tracing."""
        self._graph_patch_service.patch_all()

        self._client.is_vectice_client_valid()
        # Start tracing first
        CodeTraceService.__enter__(self)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # pyright: ignore[reportMissingParameterType]
        """Enhanced context manager that handles logging of assets and tracing cleanup."""
        CodeTraceService.__exit__(self, exc_type, exc_val, exc_tb)
        try:
            self._log_all_assets()
        except Exception as e:
            # Log API errors but don't prevent trace cleanup
            warnings.warn(f"Error during Vectice trace logging: {e}", RuntimeWarning, 1)
        finally:
            # Ensure cleanup of the graph patch service
            self._graph_patch_service.unpatch_all()
            return False

    #### Configuration ####

    def config(
        self, phase: str | None = None, prefix: str | None = None, create_new_iteration: bool | None = None
    ) -> VecticeTrace:
        """Configures the trace functionality within Vectice.

        The `config` method allows you to configure your Vectice trace by specifying the phase in which you want to trace your work.

        ```python
        # Configure trace functionality
        import vectice

        trace = vectice.trace()
        trace = trace.config(
            phase = 'PHA-XXX',           # Paste your Phase Id
            create_new_iteration = True
        )
        ```
        Parameters:
                phase: The ID of the phase in which you wish to autolog your work as an iteration.
                prefix: A Prefix which will be applied to logged models and datasets variable name. e.g `my-prefix` will be `my-prefix-variable`,
                    an empty string will be `variable` and no prefix will be `PHA-XXX-variable`.
                create_new_iteration: If set to False, logging of assets will happen in the last updated iteration. Otherwise, it will create a new iteration for logging the cell's assets.
        """
        self._client.config(phase, create_new_iteration)
        if prefix:
            self._prefix = prefix
        return self

    #### Utility Methods ####

    def _get_vectice_objects(self):
        """Get the Vectice objects that are currently being traced."""
        supported_types = (Dataset, Model, Table)
        vectice_assets = [asset for asset in self.captured_variables.values() if isinstance(asset, supported_types)]
        return vectice_assets

    def _is_ipython_environment(self) -> bool:
        """Prevent the Vectice Trace from being used in Jupyter Notebook environments."""
        try:
            from IPython.core.getipython import get_ipython

            ipython = get_ipython()
            return True if ipython else False
        except ImportError:
            pass
        return False

    #### Logging Methods ####

    def _log_all_assets(self) -> None:
        """Log all Vectice assets to the current iteration."""
        if not self._client.iteration_service:
            _logger.warning("No active iteration found.")
            return

        assets_to_log = self._get_vectice_objects()

        for asset in assets_to_log:
            self._log_vectice_asset(asset)

        patched_graphs = self._graph_patch_service.graphs
        if patched_graphs:
            self._log_graphs(patched_graphs)

        self._client.save_autolog_assets(cells=self.code, prefix=self._prefix, is_trace=True)

        if len(self._failed_assets):
            _logger.warning("The following assets failed to log:")
        for failed_asset in self._failed_assets:
            _logger.warning(f"{failed_asset['type']} {failed_asset['asset']!r}, reason: {failed_asset['reason']}")

    def _log_vectice_asset(self, asset_to_log: Dataset | Table | Model) -> None:
        """Log a Vectice asset to the current iteration."""
        try:
            asset_to_log.name = get_asset_name(str(asset_to_log.name), self._client.phase.name, self._prefix)
            object_name = asset_to_log.name

            if isinstance(asset_to_log, Dataset):
                self._client.iteration_service.log_dataset(asset_to_log)
                _logger.info(f"Dataset {object_name!r} logged in iteration {self._client.iteration.name!r}.")
            elif isinstance(asset_to_log, Table):
                self._client.iteration_service.log_table(asset_to_log)
                _logger.info(f"Table {object_name!r} logged in iteration {self._client.iteration.index!r}.")
            else:
                if asset_to_log.predictor:
                    self._client.iteration._assign_model_predictor_metadata(  # pyright: ignore[reportPrivateUsage]
                        asset_to_log
                    )
                self._client.iteration_service.log_model(asset_to_log)
                _logger.info(f"Model {object_name!r} logged in iteration {self._client.iteration.index!r}.")
        except Exception as e:
            self._failed_assets.append({"reason": e, "asset": asset_to_log, "type": type(asset_to_log).__name__})

    def _log_graphs(self, graphs: list[str]) -> None:
        for graph in graphs:
            try:
                self._client.iteration_service.log_image_or_file(graph)
                _logger.info(f"Graph {graph!r} logged in iteration {self._client.iteration.name!r}.")
            except Exception as e:
                self._failed_assets.append({"reason": e, "asset": graph, "type": "Graph"})
