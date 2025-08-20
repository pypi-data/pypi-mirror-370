from __future__ import annotations

import logging
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar

from rich.table import Table

from vectice.models.phase import Phase
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.issue_representation import IssueRepresentation
from vectice.models.representation.model_representation import ModelRepresentation
from vectice.models.representation.report_representation import ReportRepresentation
from vectice.utils.api_utils import DEFAULT_MAX_SIZE, DEFAULT_NUMBER_OF_ITEMS
from vectice.utils.common_utils import temp_print
from vectice.utils.logging_utils import get_phase_status

if TYPE_CHECKING:
    from vectice import Connection
    from vectice.models import Workspace


_logger = logging.getLogger(__name__)


class Project:
    """Represent a Vectice project.

    A project reflects a typical Data Science project, including
    phases and the associated assets like code, datasets, models, and
    documentation. Multiple projects may be defined within each workspace.

    You can get a project from your [`Workspace`][vectice.models.Workspace]
    object by calling `project()`:

    ```python
    import vectice

    connect = vectice.connect(...)
    workspace = connect.workspace("Iris workspace")
    project = workspace.project("Iris project")
    ```

    Or you can get it directly when connecting to Vectice:

    ```python
    import vectice

    project = vectice.connect(..., workspace="Iris workspace", project="Iris project")
    ```

    See [`Connection.connect`][vectice.Connection.connect] to learn
    how to connect to Vectice.
    """

    __slots__: ClassVar[list[str]] = ["_id", "_workspace", "_name", "_description", "_phase", "_client", "_pointers"]

    def __init__(
        self,
        id: str,
        workspace: Workspace,
        name: str,
        description: str | None = None,
    ):
        self._id = id
        self._workspace = workspace
        self._name = name
        self._description = description
        self._phase: Phase | None = None
        self._client = workspace._client  # pyright: ignore[reportPrivateUsage]

    def __repr__(self):
        description = self._description if self._description else "None"
        return f"Project(name={self.name!r}, id={self._id}, description={description!r}, workspace={self._workspace!r})"

    def __eq__(self, other: object):
        if not isinstance(other, Project):
            return NotImplemented
        return self.id == other.id

    @property
    def id(self) -> str:
        """The project's id.

        Returns:
            The project's id.
        """
        return self._id

    @property
    def workspace(self) -> Workspace:
        """The workspace to which this project belongs.

        Returns:
            The workspace to which this project belongs.
        """
        return self._workspace

    @property
    def connection(self) -> Connection:
        """The Connection to which this project belongs.

        Returns:
            The Connection to which this project belongs.
        """
        return self._workspace.connection

    @property
    def name(self) -> str:
        """The project's name.

        Returns:
            The project's name.
        """
        return self._name

    @property
    def description(self) -> str | None:
        """The project's description.

        Returns:
            The project's description.
        """
        return self._description

    @property
    def properties(self) -> dict:
        """The project's identifiers.

        Returns:
            A dictionary containing the `name`, `id` and `workspace` items.
        """
        return {"name": self.name, "id": self.id, "workspace": self.workspace.id}

    def phase(self, phase: str) -> Phase:
        """Get a phase.

        Parameters:
            phase: The name or id of the phase to get.

        Returns:
            The specified phase.
        """
        item = self._client.get_phase(phase, project_id=self._id)
        phase_object = Phase(item, self, self._client)
        logging_output = dedent(
            f"""
                        Phase {item.name!r} successfully retrieved.

                        For quick access to the Phase in the Vectice web app, visit:
                        {self._client.auth.api_base_url}/browse/phase/{phase_object.id}"""
        ).lstrip()
        _logger.info(logging_output)

        self._phase = phase_object
        return phase_object

    def create_phase(self, name: str, description: str | None = None) -> Phase:
        """Creates a phase.

        Parameters:
            name: The phase's name.
            description: The phase's description.

        Returns:
            The newly created phase.
        """
        item = self._client.create_phase(
            self.id,
            {"name": name, "description": description},
        )
        logging_output = dedent(
            f"""
                Phase {item.name!r} successfully created.
                For quick access to the Phase in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/phase/{item.id}"""
        ).lstrip()
        _logger.info(logging_output)
        phase_object = Phase(item, self, self._client)
        return phase_object

    def list_phases(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS, display_print: bool = True) -> list[Phase]:
        """Retrieves a list of phases belonging to the project. It will also print the first 10 phases as a tabular form. A link is provided to view the remaining phases.

        Parameters:
            number_of_items: The number of phases to retrieve. Defaults to 30.
            display_print: If set to True, it will print the first 10 phases in a tabular form.

        Returns:
            A list of `Phase` instances corresponding to the current project.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 models will be retrieved. For additional models, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        phase_outputs = self._client.list_phases(project=self.id, size=number_of_items)

        if display_print:
            rich_table = Table(expand=True, show_edge=False)

            rich_table.add_column("Phase id", justify="left", no_wrap=True, min_width=3, max_width=5)
            rich_table.add_column("Name", justify="left", no_wrap=True, min_width=5, max_width=10)
            rich_table.add_column("Owner", justify="left", no_wrap=True, min_width=4, max_width=4)
            rich_table.add_column("Status", justify="left", no_wrap=True, min_width=4, max_width=4)
            rich_table.add_column("Iterations", justify="left", no_wrap=True, min_width=4, max_width=4)

            for phase in phase_outputs.list:
                phase_owner = phase["owner"]["name"] if phase.get("owner") else "Unassigned"
                phase_status = get_phase_status(phase.status)
                rich_table.add_row(
                    phase.id,
                    phase.name,
                    phase_owner,
                    phase_status,
                    f"{phase.active_iterations_count}/{phase.iterations_count}",
                )
            description = f"""There are {phase_outputs.total} phases in the project {self.name!r}. Only the first 10 phases are displayed in the printed table below:"""
            tips = dedent(
                """
            To access a specific phase, use \033[1mproject\033[0m.phase(Phase ID)"""
            ).lstrip()
            link = dedent(
                f"""
            For quick access to the list of phases for this project, visit:
            {self._client.auth.api_base_url}/browse/project/{self.id}"""
            ).lstrip()

            temp_print(description)
            temp_print(table=rich_table)
            temp_print(tips)
            temp_print(link)

        return [Phase(phase, self, self._client) for phase in phase_outputs.list]

    def list_models(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS) -> list[ModelRepresentation]:
        """Retrieves a list of model representations associated with the current project.
        See here: https://api-docs.vectice.com/reference/vectice/representation/model/

        Parameters:
            number_of_items: The number of models to retrieve. Defaults to 30.

        Returns:
            A list of `ModelRepresentation` instances corresponding to the models in the current project.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 models will be retrieved. For additional models, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE

        model_outputs = self._client.get_model_list(project_id=self.id, size=number_of_items)
        model_representations = [ModelRepresentation(model, self._client) for model in model_outputs.list]
        return model_representations

    def list_datasets(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS) -> list[DatasetRepresentation]:
        """Retrieves a list of dataset representations associated with the current project.
        See here: https://api-docs.vectice.com/reference/vectice/representation/dataset/

        Parameters:
            number_of_items: The number of datasets to retrieve. Defaults to 30.

        Returns:
            A list of `DatasetRepresentation` instances corresponding to the datasets in the current project.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 datasets will be retrieved. For additional datasets, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        dataset_outputs = self._client.get_dataset_list(project_id=self.id, size=number_of_items)
        dataset_representations = [DatasetRepresentation(dataset, self._client) for dataset in dataset_outputs.list]
        return dataset_representations

    def list_reports(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS) -> list[ReportRepresentation]:
        """Retrieves a list of issue representations associated with the current project.
        See here: https://api-docs.vectice.com/reference/vectice/representation/issue/
        Parameters:
            number_of_items: The number of reports to retrieve. Defaults to 30.

        Returns:
            A list of `ReportRepresentation` instances corresponding to the reports in the current project.
        """
        self._client.assert_feature_flag_or_raise("list-reports")

        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 reports will be retrieved. For additional reports, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        outputs = self._client.get_reports(self.id, "prj", number_of_items)
        reps = [ReportRepresentation(report, self._client) for report in outputs.list]
        return reps

    def list_issues(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS) -> list[IssueRepresentation]:
        """Retrieves a list of issue representations associated with the current project.
        See here: https://api-docs.vectice.com/reference/vectice/representation/issue/

        Parameters:
            number_of_items: The number of issues to retrieve. Defaults to 30.

        Returns:
            A list of `IssueRepresentation` instances corresponding to the issues in the current project.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 issues will be retrieved. For additional issues, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        outputs = self._client.get_issues(self.id, "prj", number_of_items)
        reps = [IssueRepresentation(issue, self._client) for issue in outputs.list]
        return reps
