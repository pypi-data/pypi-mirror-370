from __future__ import annotations

import logging
import logging.config
import sys
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectice.api.json.iteration import IterationStatus
    from vectice.api.json.phase import PhaseStatus


CONNECTION_LOGGING = """Welcome, {user}. You`re now successfully connected to Vectice.

To connect to a phase, copy your phase ID from your Vectice app and use connect.phase("PHA-XXXX")
To create your first iteration do iteration = connect.phase("PHA-XXXX").create_or_get_current_iteration()

If you are using a notebook you can call the help by using a Vectice returned object with the builtin notebook "?":
>> connection?

If you are using an IDE you can call the help() method on any object returned by Vectice:
>> help(connection)

{logging_output}"""

CONNECTION_WORKSPACE_LOGGING = """Welcome, {user!r}. You`re now successfully connected to the workspace {workspace_name!r} in Vectice.

To access a specific project, use \033[1mworkspace\033[0m.project(Project ID)
To get a list of projects you can access and their IDs, use \033[1mworkspace\033[0m.list_projects()

For quick access to the list of projects in the Vectice web app, visit:
{url}/browse/workspace/{workspace_id}"""

CONNECTION_PROJECT_LOGGING = """Welcome, {user!r}. You`re now successfully connected to the project {project_name!r} in Vectice.

To access a specific phase, use \033[1mproject\033[0m.phase(Phase ID)
To get a list of phases you can access and their IDs, use \033[1mproject\033[0m.list_phases()

For quick access to the list of phases in the Vectice web app, visit:
{url}/browse/project/{project_id}"""


class VecticeLoggingStream:
    """A Python stream for use with event logging APIs throughout vectice (`logger.info()`, etc.).

    This stream wraps `sys.stderr`, forwarding `write()`
    and `flush()` calls to the stream referred to by `sys.stderr` at the time of the call.
    It also provides capabilities for disabling the stream to silence event logs and
    enable propagation for pytest.
    """

    def __init__(self):
        self._enabled: bool = True

    def write(self, text: str) -> None:
        if self._enabled:
            sys.stderr.write(text)

    def flush(self):
        if self._enabled:
            sys.stderr.flush()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value


VECTICE_LOGGING_STREAM = VecticeLoggingStream()


def disable_logging():
    """Disable logging.

    Disable the `VecticeLoggingStream` used by event logging APIs throughout Vectice
    `logger.info()` silencing all subsequent event logs.
    """
    VECTICE_LOGGING_STREAM.enabled = False


def enable_logging():
    """Enable logging.

    Enable the `VecticeLoggingStream` used by event logging APIs throughout Vectice.
    This reverses the effects of `disable_logging()`.
    """
    VECTICE_LOGGING_STREAM.enabled = True


def enable_propagation():
    """Enable propagation.

    Enable the `VecticeLoggingStream` propagation used by event logging APIs throughout Vectice.
    The testing suite can use caplog to test the logging stdout.
    """
    configure_vectice_loggers("vectice", propagate=True)


def configure_vectice_loggers(root_module_name: str, propagate: bool = False):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "vectice_formatter": {
                    "format": None,
                    "datefmt": None,
                },
            },
            "handlers": {
                "vectice_handler": {
                    "formatter": "vectice_formatter",
                    "class": "logging.StreamHandler",
                    "stream": VECTICE_LOGGING_STREAM,
                },
            },
            "loggers": {
                root_module_name: {
                    "handlers": ["vectice_handler"],
                    "level": "INFO",
                    "propagate": propagate,
                },
            },
        }
    )


def format_description(description: str | None) -> str | None:
    if not description:
        return None
    return description


def get_iteration_status(status: IterationStatus, starred: bool | None = None) -> str:
    verbose_dict: dict[str, str | None] = defaultdict(lambda: None)
    verbose_dict["NotStarted"] = "To Do"
    verbose_dict["InProgress"] = "In Progress"
    verbose_dict["Abandoned"] = "Cancelled"
    verbose_dict["Completed"] = "Completed"
    verbose_dict["InReview"] = "In Review"

    status_value = verbose_dict[status.value]
    if status_value is None:
        raise ValueError("Iteration status unknown")
    if starred is True:
        return status_value + " (*)"
    return status_value


def get_phase_status(status: PhaseStatus) -> str:
    verbose_dict: dict[str, str | None] = defaultdict(lambda: None)
    verbose_dict["NotStarted"] = "Not Started"
    verbose_dict["Draft"] = "In Progress"
    verbose_dict["InReview"] = "In Review"
    verbose_dict["Completed"] = "Completed"

    status_value = verbose_dict[status.value]
    if status_value is None:
        raise ValueError("Phase status unknown")
    return status_value


def get_review_status(status: str) -> str:
    verbose_dict: dict[str, str | None] = defaultdict(lambda: None)
    verbose_dict["Rejected"] = "Rejected"
    verbose_dict["Approved"] = "Approved"
    verbose_dict["Pending"] = "In Review"
    verbose_dict["Cancelled"] = "Cancelled"

    status_value = verbose_dict[status]
    if status_value is None:
        raise ValueError("Review status unknown")
    return status_value
