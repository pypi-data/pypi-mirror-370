"""Vectice package.

The Vectice package is a library allowing data-scientists
to record their progress in the [Vectice app](https://docs.vectice.com/).

This package exposes essential Vectice classes and methods:

- the [autolog][vectice.autolog.autolog] method
- the [connect][vectice.Connection.connect] method
- the [Workspace][vectice.models.Workspace] class
- the [Project][vectice.models.Project] class
- the [Phase][vectice.models.Phase] class
- the [Iteration][vectice.models.Iteration] class
- the [Dataset][vectice.Dataset] class
- the [Model][vectice.Model] class
- the [Table][vectice.Table] class

    NOTE: **IMPORTANT INFORMATION**
        Vectice calculates dataframe statistics only if the dataframe contains more than a hundred rows for privacy reasons. Those statistics are calculate on a sample of a million rows and on the first 400 columns by default. All of these values can be changed on the Organization Settings page by the organization admin.

"""

from __future__ import annotations

import sys
import warnings
from importlib.util import find_spec

warnings.filterwarnings("ignore", ".*PYARROW_IGNORE_TIMEZONE")
if sys.version_info < (3, 8):
    print(
        "ImportWarning: Python 3.7 is no longer maintained by the community. Upgrade to Python 3.8 or higher to ensure full compatibility with Vectice and access to its complete features."
    )

is_h2o = find_spec("h2o") is not None
if is_h2o:
    warnings.warn(
        "h2o is installed, autolog unsaved graphs logging will be disabled. Please save h2o plots to enable the autolog graph functionality.",
        Warning,
    )

from vectice import api, autolog, models
from vectice.__version__ import __version__
from vectice.connection import Connection
from vectice.models.dataset import Dataset
from vectice.models.model import Metric, Model, Property
from vectice.models.resource import (
    BigQueryResource,
    DatabricksTableResource,
    DFResource,
    FileResource,
    GCSResource,
    NoResource,
    Resource,
    S3Resource,
    SnowflakeResource,
    SparkTableResource,
)
from vectice.models.resource.metadata import (
    DatasetSourceOrigin,
    DatasetSourceUsage,
    DatasetType,
    DBMetadata,
    File,
    FilesMetadata,
    MetadataDB,
)
from vectice.models.table import Table
from vectice.trace.vectice_trace import VecticeTrace
from vectice.utils.load_from_settings import load_from_settings
from vectice.utils.logging_utils import configure_vectice_loggers, disable_logging

trace = VecticeTrace
connect = Connection.connect

code_capture = True

"""Global code capture flag, enabled by default.

Code capture is triggered when registering a dataset or a model,
and only works when a valid Git repository is found.
Otherwise a warning is logged, telling what might be misconfigured in the repository.

Captured information include the repository name, URL, branch name, commit hash,
and whether the repository is dirty (has uncommitted changes).

Examples:
    To disable code capture globally:

    >>> import vectice
    >>> vectice.code_capture = False

    To re-enable code capture globally:

    >>> import vectice
    >>> vectice.code_capture = True
"""

code_file_capture = False

"""Global code file capture flag, disabled by default.

Controls whether code file is captured when logging asset into Vectice as part of the lineage.
When enabled (set to True), logging an asset will also add the executed file to its lineage.
Enabling this feature may increase API runtime due to file transfer. Databricks is currently not supported.


Examples:
    To enable code_file_capture globally:

    >>> import vectice
    >>> vectice.code_file_capture = True

    To re-enable code file capture globally:

    >>> import vectice
    >>> vectice.code_file_capture = False
"""

auto_extract = True
"""Global auto extraction flag, enabled by default.

Extraction is automatically performed when registering a dataset or a model with an attachment. Currently, it exclusively operates on Excel files and extracts sheets (as CSV files) and images to be referenced inside Vectice.

Examples:
    To disable auto extraction of files globally globally:

    >>> import vectice
    >>> vectice.auto_extract = False

    To re-enable auto extraction globally:

    >>> import vectice
    >>> vectice.auto_extract = True
"""

pickle_capture = True
"""Global pickle capture flag, enabled by default.

Pickle capture is triggered when registering a Vectice Model and only works when a valid predictor parameter is passed or when Autolog detects an estimator,
for example a scikit-learn regressor. The predictor is pickled and attached to the Model Version in Vectice. 

Examples:
    To disable pickle capture globally:

    >>> import vectice
    >>> vectice.pickle_capture = False

    To re-enable pickle capture globally:

    >>> import vectice
    >>> vectice.pickle_capture = True
    
    Standard API
    
    >>> from vectice import Model
    ...
    >>> my_estimator = LinearRegression()
    >>> model = Model(predictor=my_estimator)
    
    Autolog
    
    >>> from vectice import autolog
    ...
    >>> my_estimator = LinearRegression()
    >>> autolog.cell()
    
"""

configure_vectice_loggers(root_module_name=__name__)
silent = disable_logging
# Ignore all deprecation warnings by default
warnings.simplefilter("ignore", DeprecationWarning)
# But show them for vectice modules
warnings.filterwarnings("always", category=DeprecationWarning, module="vectice.*")

version = __version__

__all__ = [
    "BigQueryResource",
    "DBMetadata",
    "DFResource",
    "DatabricksTableResource",
    "Dataset",
    "DatasetSourceOrigin",
    "DatasetSourceUsage",
    "DatasetType",
    "File",
    "FileResource",
    "FilesMetadata",
    "GCSResource",
    "MetadataDB",
    "Metric",
    "Model",
    "NoResource",
    "Property",
    "Resource",
    "S3Resource",
    "SnowflakeResource",
    "SparkTableResource",
    "Table",
    "api",
    "autolog",
    "connect",
    "load_from_settings",
    "models",
    "silent",
    "version",
]
