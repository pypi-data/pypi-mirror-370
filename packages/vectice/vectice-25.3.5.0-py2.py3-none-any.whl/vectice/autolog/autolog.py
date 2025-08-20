"""Auto-Logging assets with Vectice.

NOTE: **IMPORTANT INFORMATION**
    Your feedback is highly valued. Please send any feedback to support@vectice.com.

------------
The autolog feature in Vectice allows for seamless documentation and management of your data science projects. Please note the following details about this feature.

NOTE: **This feature is designed to work specifically with notebooks.**

1.** Installation:**
    Make sure you install Vectice package using the following command:

    ```bash
    pip install vectice
    ```

2.** Supported libraries and environment:**
    Vectice automatically identifies and log assets encapsulated within a specified list of supported libraries and environement mentioned below

NOTE: **Supported libraries and environment**
    - Dataframe: Pandas, Spark.
    - Model: Scikit, Xgboost, Lightgbm, Catboost, Keras, Pytorch, Statsmodels, Pyspark MLlib, H2O.
    - Validation: Giskard.
    - Graphs: Matplotlib, Seaborn, Plotly, H2O.
    - Environments: Colab, Jupyter, Vertex, SageMaker, Databricks, Pycharm and VScode notebook.

3.** General behavior:**
    Vectice autolog provides three methods: `autolog.config`, `autolog.notebook`, and `autolog.cell`. These methods are designed to log every asset to Vectice existing as a variable in the notebook's memory. It is important to review the specific behaviors outlined in the documentation for each of these three methods.

NOTE: **IMPORTANT INFORMATION**
    - For GRAPHS, ensure they are saved as files or the plot is displayed to be automatically logged in the iteration i.e
        - In inline environments like Jupyter Lab and Jupyter Hub (not IDEs), using `plt.show()` can flush the canvas, potentially preventing displayed or saved graphs from being captured.
          To avoid this, use only `plt.savefig()` to save your figures instead of or before calling `plt.show()`.
          See here: https://matplotlib.org/stable/users/explain/figure/interactive.html
        - fig.write_image("my figure.png") (for plotly)
    - For METRICS, Vectice currently recognizes sklearn, Pyspark and H2O metrics for automatic association with models.
        - In cases there's ambiguity due to multiple models with different metrics, Vectice won't automatically link them. To establish the link, make sure each model and its respective metrics are placed within the same notebook cell.
        - H2O scoring metric functions that generate metric tables (e.g., `h2o.confusion_matrix`) are automatically logged. Some functions require `as_data_frame=False` to return a H2oDisplay object, which is then logged as a table asset.
    - For VALIDATION, Vectice currently supports Giskard for validation.
        See here: https://docs.giskard.ai/en/stable/

"""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Callable

from typing_extensions import TypedDict

from vectice.api.http_error_handlers import VecticeException
from vectice.models.iteration import Iteration

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell

    from vectice.connection import Connection
    from vectice.models import Phase


class Login(TypedDict):
    phase: Phase | None
    prefix: str | None


LOGIN: Login = {"phase": None, "prefix": None}

_logger = logging.getLogger(__name__)


def vectice_config():
    vectice_config = os.environ.get("VECTICE_CONFIG")
    if vectice_config is None:
        raise ValueError(
            "Use from vectice import load_from_settings to configure autolog using the environmental variable."
        )

    config_dict = json.loads(vectice_config)

    api_token, host, phase = config_dict["api_token"], config_dict["host"], config_dict["phase"]
    config(api_token, phase, host)


# Setup vectice connection on phase
def config(api_token: str, phase: str, host: str | None = None, prefix: str | None = None) -> None:
    """Configures the autolog functionality within Vectice.

    The `config` method allows you to establish a connection to Vectice and specify the phase in which you want to autolog your work.

    ```python
    # Configure autolog
    from vectice import autolog
    autolog.config(
        api_token = 'your-api-key', # Paste your api key
        phase = 'PHA-XXX'           # Paste your Phase Id
    )
    ```

    Parameters:
            api_token: The api token provided inside your Vectice app (API key).
            phase: The ID of the phase in which you wish to autolog your work as an iteration.
            host: The backend host to which the client will connect. If not found, the default endpoint https://app.vectice.com is used.
            prefix: A Prefix which will be applied to logged models and datasets variable name. e.g `my-prefix` will be `my-prefix-variable`,
                    an empty string will be `variable` and no prefix will be `PHA-XXX-variable`.

    """
    from vectice import Connection
    from vectice.connection import DEFAULT_HOST

    host = host or DEFAULT_HOST
    vec = Connection(api_token=api_token, host=host)
    client = vec._client  # pyright: ignore[reportPrivateUsage]
    asset = client.get_user_and_default_workspace()
    user_name = asset["user"]["name"]
    _logger.info(f"Welcome, {user_name}. You`re now successfully connected to Vectice.")
    LOGIN["phase"] = vec.phase(phase)
    LOGIN["prefix"] = prefix
    _logger.warning(
        "\nFor detailed information about autolog, supported libraries and environments please consult the documentation: https://api-docs.vectice.com/reference/vectice/autolog/"
    )
    from vectice.autolog.autolog_class import start_listen, validate_ipython_session

    ipython = start_listen()
    if validate_ipython_session(ipython) is False:
        _logger.warning(
            "\nNew Ipython session detected, autolog graphs have been reset. This is most likely due to opening and closing the jupyter browser. Please re-run the cells which contain your graphs. A kernel restart and autolog.config is not required."
        )


def phase_config(phase: str | None = None) -> None:
    """Update the phase in which autolog is logging assets. (This method will update the configured phase defined in autolog.config).

    If phase is None, the method print the current configured phase.

    NOTE: **Ensure that you have configured the autolog with your Vectice API token before using this method.**

    ```python
    # After autolog is configured
    autolog.phase_config(
        phase = 'PHA-XXX'   # Paste your Phase Id
    )
    ```

    Parameters:
            phase: The ID of the phase in which you wish to autolog your work as an iteration.

    """
    if LOGIN["phase"] is None:
        _logger.warning("\nAutolog needs to be configured before using this method. Please run autolog.config() first.")
    else:
        if phase is None:
            _logger.info(
                f"\nCurrent configured phase name is: `{LOGIN['phase'].name}`"
                f"\nCurrent configured phase ID is: `{LOGIN['phase'].id}`"
            )
            return None
        else:
            LOGIN["phase"] = LOGIN["phase"].connection.phase(phase)


def iteration() -> Iteration | None:
    """Get the last iteration that was updated. Allowing you to retrieve your workable iteration to complete it or list assets.

    NOTE: **Ensure that you have configured the autolog with your Vectice API token before using this method.**

    ```python
    # After autolog is configured
    autolog.iteration()
    ```
    """
    from vectice.services.phase_service import PhaseService

    if LOGIN["phase"] is None:
        _logger.warning("\nAutolog needs to be configured before using this method. Please run autolog.config() first.")
        return None
    else:
        iteration = PhaseService(
            LOGIN["phase"]._client  # pyright: ignore[reportPrivateUsage]
        ).get_active_iteration_or_create(LOGIN["phase"])
    return iteration


# Log the whole notebook inside Vectice iteration
def notebook(
    note: str | None = None,
    capture_schema_only: bool = True,
    capture_comments: bool = True,
    capture_widget_graphs: bool = True,
    organize_with_ai: bool = False,
) -> None:
    """Automatically log all supported models, dataframes, and graphs from your notebook within the Vectice App as assets.

    NOTE: **IMPORTANT INFORMATION**
        Autolog must be configured at the beginning of your notebook to capture all relevant information. Cells executed prior to configuring autolog may not have their assets recorded by the autolog.notebook() method and may need to be run again.

    ```python
                                   ...
    #Add this command at the end of notebook to log all the assets in memory
    autolog.notebook()
    ```

    NOTE: **Ensure that the required assets are in memory before calling this method.**

    Parameters:
        note: the note or comment to log to your iteration associated with the autolog.notebook
        capture_schema_only: A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes. If set to False, both the schema and column statistics of the dataframes will be captured. Please note that this option may require additional processing time due to the computation of statistics.
        capture_comments: A boolean parameter indicating whether comments should be automatically logged as notes inside Vectice. If set to True, autolog will capture all comments that start with '##'.
        capture_widget_graphs: A boolean parameter indicating whether widget graphs should be automatically logged as images inside Vectice. If set to True, autolog will capture all widget graphs.
        organize_with_ai: A boolean parameter indicating whether the iteration should be automatically organized with AI.
    """
    from vectice.autolog.autolog_class import Autolog, validate_ipython_session

    # TODO add notebook parsing of content
    ipython = _check_if_notebook()
    if validate_ipython_session(ipython) is False:
        raise VecticeException(
            "New Ipython session detected, autolog graphs have been reset. This is most likely due to opening and closing the jupyter browser. Please re-run the cells which contain your graphs. A kernel restart and autolog.config is not required."
        )

    Autolog(
        LOGIN["phase"],
        ipython,
        True,
        True,
        note,
        capture_schema_only,
        capture_comments,
        LOGIN["prefix"],
        capture_widget_graphs,
        organize_with_ai,
    )


def cell(
    create_new_iteration: bool = False,
    note: str | None = None,
    capture_schema_only: bool = True,
    capture_comments: bool = True,
    capture_widget_graphs: bool = False,
):
    """Automatically logs all supported models, dataframes, and graphs from a specific notebook cell within the Vectice platform.

    This method facilitates the selective logging of assets within a particular notebook cell, allowing users to precisely choose the assets to log to Vectice with an optional control to log assets inside a new iteration.

    NOTE: **Ensure that you have configured the autolog with your Vectice API token and the relevant phase ID before using this method.**

    ```python
                                   ...
    #Add this command at the end of the desired cell to log all the cells assets
    autolog.cell()
    ```

    NOTE: **Place the command at the end of the desired cell to log all assets within that cell.**

    Parameters:
        create_new_iteration: If set to False, logging of assets will happen in the last updated iteration. Otherwise, it will create a new iteration for logging the cell's assets.
        note: the note or comment to log to your iteration associated with the autolog.cell
        capture_schema_only: A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes. If set to False, both the schema and column statistics of the dataframes will be captured. Please note that this option may require additional processing time due to the computation of statistics.
        capture_comments: A boolean parameter indicating whether comments should be automatically logged as notes inside Vectice. If set to True, autolog will capture all comments that start with '##'.
        capture_widget_graphs: A boolean parameter indicating whether widget graphs should be automatically logged as images inside Vectice. If set to True, autolog will capture all widget graphs.

    """
    from vectice.autolog.autolog_class import Autolog, validate_ipython_session

    ipython = _check_if_notebook()
    if validate_ipython_session(ipython) is False:
        raise VecticeException(
            "New Ipython session detected, autolog graphs have been reset. This is most likely due to opening and closing the jupyter browser. Please re-run the cells which contain your graphs. A kernel restart and autolog.config is not required."
        )

    Autolog(
        LOGIN["phase"],
        ipython,
        False,
        create_new_iteration,
        note,
        capture_schema_only,
        capture_comments,
        LOGIN["prefix"],
        capture_widget_graphs,
    )


def get_connection() -> Connection:
    """Get the Connection from autolog.config(...) to interact with the Vectice base Python API.

    NOTE: **Ensure that you have configured the autolog with your Vectice API token and the relevant phase ID before using this method.**

    ```python
                                   ...
    #After autolog is configured
    connect = autolog.get_connection()
    ```
    """
    phase = LOGIN["phase"]
    if phase:
        return phase.connection

    raise ConnectionError("Autolog needs to be configured before using this method. Please run autolog.config() first.")


def _check_if_notebook() -> InteractiveShell:
    from IPython.core.getipython import get_ipython

    ipython = get_ipython()

    if ipython is None:
        raise ValueError("Not a notebook.")
    return ipython


def add_custom_metric_function(func: Callable) -> Callable:
    """Custom metric decorator, to flag custom metric functions to be logged by autolog.

    NOTE: **Ensure that the return type of the custom metric function is an integer or float.**

    ```python
     ...
    from vectice.autolog import add_custom_metric

    @add_custom_metric_function
    def my_custom_metric(...):
      return 21

    some_predictor = ....
    custom_metric = my_custom_metric(...)

    autolog.cell()
    ```
    """
    # simple decorator to mark custom metric functions
    func.custom_metric_function = True  # pyright: ignore[reportFunctionMemberAccess]
    return func


# Log the whole notebook inside Vectice iteration, + run organize with ask ai + generate a report
def generate_doc(
    note: str | None = None,
    capture_schema_only: bool = True,
    capture_comments: bool = True,
    capture_widget_graphs: bool = True,
) -> None:
    """Automatically log all supported models, dataframes, and graphs from your notebook within the Vectice App as assets, then use AI to organize the iteration and generate a report.

    NOTE: **IMPORTANT INFORMATION**
        Autolog must be configured at the beginning of your notebook to capture all relevant information. Cells executed prior to configuring autolog may not have their assets recorded by the autolog.generate_doc() method and may need to be run again.

    ```python
                                   ...
    #Add this command at the end of notebook to log all the assets in memory
    autolog.generate_doc()
    ```

    NOTE: **Ensure that the required assets are in memory before calling this method.**

    Parameters:
        note: the note or comment to log to your iteration associated with the autolog.notebook
        capture_schema_only: A boolean parameter indicating whether to capture only the schema or both the schema and column statistics of the dataframes. If set to False, both the schema and column statistics of the dataframes will be captured. Please note that this option may require additional processing time due to the computation of statistics.
        capture_comments: A boolean parameter indicating whether comments should be automatically logged as notes inside Vectice. If set to True, autolog will capture all comments that start with '##'.
        capture_widget_graphs: A boolean parameter indicating whether widget graphs should be automatically logged as images inside Vectice. If set to True, autolog will capture all widget graphs.
    """
    from vectice.autolog.autolog_class import Autolog, validate_ipython_session

    # TODO add notebook parsing of content
    ipython = _check_if_notebook()
    if validate_ipython_session(ipython) is False:
        raise VecticeException(
            "New Ipython session detected, autolog graphs have been reset. This is most likely due to opening and closing the jupyter browser. Please re-run the cells which contain your graphs. A kernel restart and autolog.config is not required."
        )

    Autolog(
        LOGIN["phase"],
        ipython,
        True,
        True,
        note,
        capture_schema_only,
        capture_comments,
        LOGIN["prefix"],
        capture_widget_graphs,
        True,
        True,  # organize with AI and generate report
    )
