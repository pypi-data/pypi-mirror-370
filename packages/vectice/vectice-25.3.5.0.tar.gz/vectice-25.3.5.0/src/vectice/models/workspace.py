from __future__ import annotations

import logging
from textwrap import dedent
from typing import TYPE_CHECKING

from rich.table import Table

from vectice.models.project import Project
from vectice.models.representation.project_template import ProjectTemplate
from vectice.utils.api_utils import DEFAULT_MAX_SIZE, DEFAULT_NUMBER_OF_ITEMS, DEFAULT_PRINT_SIZE
from vectice.utils.common_utils import temp_print
from vectice.utils.logging_utils import format_description

if TYPE_CHECKING:
    from vectice import Connection
    from vectice.api import Client


_logger = logging.getLogger(__name__)


class Workspace:
    """Represent a Vectice Workspace.

    Workspaces are containers used to organize projects, assets, and
    users.

    Vectice users have access to a personal workspace and other
    workspaces so they can learn and collaborate with other users. An
    organization will have many workspaces, each with an Admin and
    Members with different privileges.

    Note that only an Org Admin can create a new workspace in the
    organization.

    You can get a workspace from your [`Connection`][vectice.Connection]
    object by calling `workspace()`:

    ```python
    import vectice

    connect = vectice.connect(...)
    workspace = connect.workspace("Iris workspace")
    ```

    Or you can get it directly when connecting to Vectice:

    ```python
    import vectice

    workspace = vectice.connect(..., workspace="Iris workspace")
    ```

    See [`Connection.connect`][vectice.Connection.connect] to learn
    how to connect to Vectice.
    """

    def __init__(self, id: str, name: str, description: str | None = None):
        self._id = id
        self._name = name
        self._description = description
        self._client: Client
        self._connection: Connection

    def __post_init__(self, client: Client, connection: Connection):
        self._client = client
        self._connection = connection

    def __eq__(self, other: object):
        if not isinstance(other, Workspace):
            return NotImplemented
        return self.id == other.id

    def __repr__(self):
        description = self._description if self._description else "None"
        return f"Workspace(name={self.name!r}, id={self._id}, description={description!r})"

    @property
    def id(self) -> str:
        """The workspace's id.

        Returns:
            The workspace's id.
        """
        return self._id

    @property
    def name(self) -> str:
        """The workspace's name.

        Returns:
            The workspace's name.
        """
        return self._name

    @property
    def description(self) -> str | None:
        """The workspace's description.

        Returns:
            The workspace's description.
        """
        return self._description

    @property
    def properties(self) -> dict:
        """The workspace's name and id.

        Returns:
            A dictionary containing the `name` and `id` items.
        """
        return {"name": self.name, "id": self.id}

    def project(self, project: str) -> Project:
        """Get a project.

        Parameters:
            project: The project name or id.

        Returns:
            The project.
        """
        item = self._client.get_project(project, self.id)
        logging_output = dedent(
            f"""
                Project {item.name!r} successfully retrieved.

                For quick access to the Project in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/project/{item.id}"""
        ).lstrip()
        _logger.info(logging_output)
        project_object = Project(item.id, self, item.name, item.description)
        return project_object

    def list_projects(
        self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS, display_print: bool = True
    ) -> list[Project]:
        """Retrieves a list of projects belonging to the workspace. It will also print the first 10 projects as a tabular form.

        Parameters:
            number_of_items: The number of datasets to retrieve. Defaults to 30.
            display_print: If set to True, it will print the first 10 projects in a tabular form.

        Returns:
            A list of `Project` instances.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 projects will be retrieved. For additional projects, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        project_outputs = self._client.list_projects(self.id, size=number_of_items)
        project_list = [
            Project(project.id, self, project.name, project.description) for project in project_outputs.list
        ]

        if display_print:
            rich_table = Table(expand=True, show_edge=False)

            rich_table.add_column("Name", justify="left", no_wrap=True, max_width=15)
            rich_table.add_column("Description", justify="left", no_wrap=True, max_width=50)

            for project in project_outputs.list[:DEFAULT_PRINT_SIZE]:
                rich_table.add_row(project.id, project.name, format_description(project.description))

            description = dedent(
                f"""
            There are {project_outputs.total} projects in the workspace {self.name!r}. Only the first 10 projects are displayed in the printed table below:
            """
            ).lstrip()
            tips = dedent(
                """
            To access a specific project, use \033[1mworkspace\033[0m.project(Project ID)"""
            ).lstrip()
            link = dedent(
                f"""
                For quick access to the list of projects in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/workspace/{self.id}"""
            ).lstrip()

            temp_print(description)
            temp_print(table=rich_table)
            temp_print(tips)
            temp_print(link)

        return project_list

    def create_project(
        self, name: str, description: str | None = None, template: str | None = None, copy_project_id: str | None = None
    ) -> Project:
        """Creates a project.

        Parameters:
            name: The project's name.
            description: The project's description.
            template: Creates the project from a spectific template. Available templates options : `tutorial`, `quickstart`, `default` (crisp-dm).
            copy_project_id: Creates the project from another project using the id `PRJ-XXX`. If template parameter is passed, it will take precedent over the project id.

        Returns:
            The newly created project.
        """
        if template is not None and copy_project_id is not None:
            _logger.warning(
                "Both template and copy_project_id parameters have been passed, template will take precedent over the project id."
            )

        item = self._client.create_project(
            self.id,
            {"name": name, "description": description, "template": template, "copy_project_id": copy_project_id},
        )
        logging_output = dedent(
            f"""
                Project {item.name!r} successfully created.

                For quick access to the Project in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/project/{item.id}"""
        ).lstrip()
        _logger.info(logging_output)
        project_object = Project(item.id, self, item.name, item.description)
        return project_object

    @property
    def connection(self) -> Connection:
        """The Connection to which this workspace belongs.

        Returns:
            The Connection to which this workspace belongs.
        """
        return self._connection

    def list_templates(self, display_print: bool = True) -> list[ProjectTemplate]:
        """Retrieves a list of project templates which belong to the workspace. It will also print the first 10 project templates as a tabular form.

        Parameters:
            display_print: If set to True, it will print the first 10 project templates in a tabular form.

        Returns:
            A list of `ProjectTemplate` instances.
        """
        project_template_outputs = self._client.list_templates()
        project_template_list = [
            ProjectTemplate(project.name, project.description) for project in project_template_outputs
        ]

        if display_print:
            rich_table = Table(expand=True, show_edge=False)

            rich_table.add_column("Name", justify="left", no_wrap=True, max_width=15)
            rich_table.add_column("Description", justify="left", no_wrap=True, max_width=50)

            for project in project_template_outputs[:DEFAULT_PRINT_SIZE]:
                rich_table.add_row(project.name, format_description(project.description))

            description = dedent(
                f"""
            There are {len(project_template_outputs)} project templates that you can use to create a project. Only the first 10 project templates are displayed in the printed table below:
            """
            ).lstrip()

            temp_print(description)
            temp_print(table=rich_table)

        return project_template_list
