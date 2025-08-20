from __future__ import annotations

import logging
import os
import re
from contextlib import suppress
from pathlib import Path
from textwrap import dedent
from typing import ClassVar, overload

import dotenv
from rich.table import Table

from vectice.api import Client
from vectice.api.http_error_handlers import InvalidIdError
from vectice.api.json.iteration import IterationOutput
from vectice.api.json.phase import PhaseOutput
from vectice.api.json.project import ProjectOutput
from vectice.api.json.workspace import WorkspaceOutput
from vectice.models.iteration import Iteration
from vectice.models.phase import Phase
from vectice.models.project import Project
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_representation import ModelRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation
from vectice.models.workspace import Workspace
from vectice.utils.api_utils import DEFAULT_MAX_SIZE, DEFAULT_NUMBER_OF_ITEMS, DEFAULT_PRINT_SIZE
from vectice.utils.common_utils import check_for_git_or_code_file, hide_logs, temp_print
from vectice.utils.configuration import Configuration
from vectice.utils.last_assets import connection_logging, get_last_user_and_default_workspace
from vectice.utils.logging_utils import CONNECTION_PROJECT_LOGGING, CONNECTION_WORKSPACE_LOGGING, format_description
from vectice.utils.vectice_ids_regex import (
    DATASET_VERSION_VID_REG,
    DATASET_VID_REG,
    ITERATION_VID_REG,
    MODEL_VERSION_VID_REG,
    MODEL_VID_REG,
    PHASE_VID_REG,
    PROJECT_VID_REG,
    WORKSPACE_VID_REG,
)

_logger = logging.getLogger(__name__)
DEFAULT_HOST = "https://app.vectice.com"
CAN_NOT_BE_EMPTY_ERROR_MESSAGE = "%s can not be empty."


class Connection:
    """Connect to the Vectice backend (application).

    The Connection class encapsulates a connection to the Vectice App.
    Thus, it authenticates and connects to Vectice.
    This allows you to start interacting with your Vectice assets.

    A Connection can be initialized in three ways:

    1. Passing the relevant arguments to authenticate and connect to Vectice:

        ```python
        import vectice

        connect = vectice.connect(
            api_token="your-api-key",
            host="https://app.vectice.com",
        )
        ```

    2. Passing the path to a configuration file:

        ```python
        import vectice

        connect = vectice.connect(config="vectice_config.json")
        ```

    3. Letting Vectice find the configuration file in specific locations:

        ```python
        import vectice

        connect = vectice.connect()
        ```

    See [`Connection.connect`][vectice.connection.Connection.connect] for more info.
    """

    USER_FILES_PATH: ClassVar[list[str]] = [
        ".vectice",
        str(Path.home() / ".vectice"),
        ".env",
        str(Path.home() / ".env"),
        "/etc/vectice/api.cfg",
    ]

    def __init__(self, api_token: str, host: str):
        from vectice import code_capture, code_file_capture, pickle_capture

        logging.getLogger("Client").propagate = True
        self._workspace: Workspace | None = None
        self._client = Client.get_instance(token=api_token, api_endpoint=host)
        compatibility = self._client.check_compatibility()
        if compatibility.status != "OK":
            if compatibility.status == "Error":
                _logger.error(f"compatibility error: {compatibility.message}")
                raise RuntimeError(f"compatibility error: {compatibility.message}")
            else:
                _logger.warning(f"compatibility warning: {compatibility.message}")

        repo_is_accessible, file_is_accessible = check_for_git_or_code_file()
        if code_capture and not repo_is_accessible:
            _logger.warning("Code capture is enabled. But no git was found.")
        if code_file_capture and not file_is_accessible:
            _logger.warning("Code file capture is enabled. But notebook or script file can not be accessed.")
        if pickle_capture is False:
            _logger.warning("Pickle capture is disabled. Model estimators will not be captured as a pickle file.")

    def __repr__(self) -> str:
        return (
            "Connection("
            + f"workspace={self._workspace.name if self._workspace else 'None'}, "
            + f"host={self._client.auth.api_base_url}, "
        )

    @property
    def version_api(self) -> str:
        return self._client.version_api

    @property
    def version_backend(self) -> str:
        return self._client.version_backend

    @property
    def my_workspace(self) -> Workspace:
        """Retrieve your personal workspace.

        Returns:
            Personal workspace.
        """
        asset = self._client.get_user_and_default_workspace()
        if not asset.get("defaultWorkspace"):
            raise ValueError("Default workspace is not set.")
        return self.workspace(asset["defaultWorkspace"]["vecticeId"])

    @overload
    @staticmethod
    def connect(  # type: ignore[misc]
        api_token: str | None = None,
        host: str | None = None,
        config: str | None = None,
        workspace: str | None = None,
        project: None = None,
    ) -> Connection | Workspace | Project: ...

    @overload
    @staticmethod
    def connect(
        api_token: str | None = None,
        host: str | None = None,
        config: str | None = None,
        workspace: str | None = None,
        project: str = "",
    ) -> Project: ...

    @staticmethod
    def connect(
        api_token: str | None = None,
        host: str | None = None,
        config: str | None = None,
        workspace: str | None = None,
        project: str | None = None,
    ) -> Connection | Workspace | Project:
        """Method to connect to the Vectice backend (application).

        Authentication credentials are retrieved, in order, from:

        1. keyword arguments
        2. configuration file (`config` parameter)
        3. environment variables
        4. environment files in the following order
            - `.vectice` of the working directory
            - `.vectice` of the user home directory
            - `.env` of the working directory
            - `.env` of the user home directory
            - `/etc/vectice/api.cfg` file

        This method uses the `api_token`, `host`, `workspace`, `project` arguments
        or the JSON config provided. The JSON config file is available from the Vectice
        webapp when creating an API token.

        Parameters:
            api_token: The api token provided by the Vectice webapp (API key).
            host: The backend host to which the client will connect.
                If not found, the default endpoint https://app.vectice.com is used.
            config: A JSON config file containing keys VECTICE_API_TOKEN and
                VECTICE_HOST as well as optionally WORKSPACE and PROJECT.
            workspace: The name or id of an optional workspace to return.
            project: The name or id of an optional project to return.

        Returns:
            A Connection, Workspace, or Project.
        """
        host = host or Connection._get_host(config)
        api_token = api_token or Connection._get_api_token(host, config)
        workspace = workspace or Connection._get_config_workspace(config)
        project = project or Connection._get_config_project(config)
        connection = Connection(api_token=api_token, host=host)
        user_name, workspace_id = get_last_user_and_default_workspace(connection._client)
        url = connection._client.auth.api_base_url
        if workspace:
            return connection._log_workspace_or_project(workspace, project, user_name, url)
        connection_logging(_logger, user_name, url, workspace_id)
        return connection

    def browse(
        self, asset: str
    ) -> (
        Workspace
        | Project
        | Phase
        | Iteration
        | DatasetRepresentation
        | ModelRepresentation
        | DatasetVersionRepresentation
        | ModelVersionRepresentation
    ):
        """Get an asset.

        Parameters:
            asset: The id of the desired asset.

        Returns:
            The desired asset.
        """
        if re.search(WORKSPACE_VID_REG, asset):
            return self.workspace(asset)
        elif re.search(PROJECT_VID_REG, asset):
            return self.project(asset)
        elif re.search(PHASE_VID_REG, asset):
            return self.phase(asset)
        elif re.search(ITERATION_VID_REG, asset):
            return self.iteration(asset)
        elif re.search(MODEL_VID_REG, asset):
            return self.model(asset)
        elif re.search(MODEL_VERSION_VID_REG, asset):
            return self.model_version(asset)
        elif re.search(DATASET_VID_REG, asset):
            return self.dataset(asset)
        elif re.search(DATASET_VERSION_VID_REG, asset):
            return self.dataset_version(asset)

        raise InvalidIdError("asset", asset)

    def workspace(self, workspace: str) -> Workspace:
        """Get a workspace.

        Parameters:
            workspace: The id or the name of the desired workspace.

        Returns:
            The desired workspace.
        """
        result = self._get_workspace_from_str(workspace)
        logging_output = dedent(
            f"""
                        Workspace {result.name!r} successfully retrieved."

                        For quick access to the workspace in the Vectice web app, visit:
                        {self._client.auth.api_base_url}/browse/workspace/{result.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return result

    def _build_workspace_from_output(self, output: WorkspaceOutput) -> Workspace:
        workspace = Workspace(output.id, output.name, output.description)
        workspace.__post_init__(self._client, self)
        return workspace

    def _build_project_from_output(self, output: ProjectOutput) -> Project:
        workspace = self._build_workspace_from_output(output.workspace)
        project = Project(output.id, workspace, output.name, output.description)
        return project

    def _build_phase_from_output(self, output: PhaseOutput) -> Phase:
        if output.project is None:
            raise RuntimeError("Failed to get back project from phase output")
        project = self._build_project_from_output(output.project)
        phase = Phase(output, project, self._client)
        return phase

    def _build_iteration_from_output(self, output: IterationOutput) -> Iteration:
        if output.phase is None:
            raise RuntimeError("Failed to get back phase from iteration output")
        phase = self._build_phase_from_output(output.phase)
        iteration = Iteration(output, phase, self._client)
        return iteration

    def project(self, project: str) -> Project:
        """Get a project.

        Parameters:
            project: The id of the desired project.

        Returns:
            The desired project.
        """
        if not re.search(PROJECT_VID_REG, project):
            raise InvalidIdError("project", project)
        output = self._get_project_from_str(project)
        logging_output = dedent(
            f"""
                Project {output.name!r} successfully retrieved.

                For quick access to the Project in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/project/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return output

    def phase(self, phase: str) -> Phase:
        """Get a phase.

        Parameters:
            phase: The id of the desired phase.

        Returns:
            The desired phase.
        """
        if not re.search(PHASE_VID_REG, phase):
            raise InvalidIdError("phase", phase)
        output = self._client.get_full_phase(phase)

        logging_output = dedent(
            f"""
                        Phase {output.name!r} successfully retrieved.

                        For quick access to the Phase in the Vectice web app, visit:
                        {self._client.auth.api_base_url}/browse/phase/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return self._build_phase_from_output(output)

    def iteration(self, iteration: str) -> Iteration:
        """Get an iteration.

        Parameters:
            iteration: The id of the desired iteration.

        Returns:
            The desired iteration.
        """
        if not re.search(ITERATION_VID_REG, iteration):
            raise InvalidIdError("iteration", iteration)
        output = self._client.get_iteration_by_id(iteration, True)
        logging_output = dedent(
            f"""
                Iteration {output.name!r} successfully retrieved.

                For quick access to the Iteration in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/iteration/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return self._build_iteration_from_output(output)

    def dataset(self, dataset: str) -> DatasetRepresentation:
        """Get a dataset.

        Parameters:
            dataset: The id of the desired dataset.

        Returns:
            The representation of the desired dataset.
        """
        if not re.search(DATASET_VID_REG, dataset):
            raise InvalidIdError("dataset", dataset)
        output = self._client.get_dataset(dataset)
        logging_output = dedent(
            f"""
                Dataset {output.name!r} successfully retrieved.

                For quick access to the Dataset in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/dataset/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return DatasetRepresentation(output, self._client)

    def dataset_version(self, version: str) -> DatasetVersionRepresentation:
        """Get a dataset version's metadata from Vectice.

        Parameters:
            version: The id of the desired dataset version. A Dataset version is identified with an ID starting with 'DTV-XXX'.

        Returns:
            The representation of the desired dataset version. (See Representation/ Dataset Version Representation).
        """
        if not re.search(DATASET_VERSION_VID_REG, version):
            raise InvalidIdError("dataset_version", version)
        output = self._client.get_dataset_version(version)
        logging_output = dedent(
            f"""
                Dataset version {output.name!r} successfully retrieved.

                For quick access to the Dataset version in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/datasetversion/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return DatasetVersionRepresentation(output, self._client)

    def model(self, model: str) -> ModelRepresentation:
        """Get a model.

        Parameters:
            model: The id of the desired model.

        Returns:
            The representation of the desired model.
        """
        if not re.search(MODEL_VID_REG, model):
            raise InvalidIdError("model", model)
        output = self._client.get_model(model)
        logging_output = dedent(
            f"""
                Model {output.name!r} successfully retrieved.

                For quick access to the Model in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/model/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return ModelRepresentation(
            output,
            self._client,
        )

    def model_version(self, version: str) -> ModelVersionRepresentation:
        """Get a model version's metadata from Vectice.

        Parameters:
            version: The id of the desired model version. A model version is identified with an ID starting with 'MDV-XXX'.

        Returns:
            The representation of the desired model version (See Representation/ Model Version Representation).
        """
        if not re.search(MODEL_VERSION_VID_REG, version):
            raise InvalidIdError("model_version", version)
        output = self._client.get_model_version(version)
        logging_output = dedent(
            f"""
                Model version {output.name!r} successfully retrieved.

                For quick access to the Model version in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/modelversion/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return ModelVersionRepresentation(output, client=self._client)

    def list_workspaces(
        self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS, display_print: bool = True
    ) -> list[Workspace]:
        """Retrieves a list of workspaces belonging where you have access to. It will also print the first 10 workspaces as a tabular form.

        Parameters:
            number_of_items: The number of workspace to retrieve. Defaults to 30.
            display_print: If set to True, it will print the first 10 workspaces in a tabular form.

        Returns:
            A list of `Workspace` instances.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 workspaces will be retrieved. For additional workspaces, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE

        workspace_outputs = self._client.list_workspaces(size=number_of_items)
        workspace_list = [self._build_workspace_from_output(workspace) for workspace in workspace_outputs.list]

        if display_print:
            rich_table = Table(expand=True, show_edge=False)
            rich_table.add_column("workspace id", justify="left", no_wrap=True, min_width=4, max_width=10)
            rich_table.add_column("name", justify="left", no_wrap=True, max_width=20)
            rich_table.add_column("description", justify="left", no_wrap=True, max_width=50)

            for workspace in workspace_outputs.list[:DEFAULT_PRINT_SIZE]:
                rich_table.add_row(str(workspace.id), workspace.name, format_description(workspace.description))

            description = dedent(
                f"""
            There are {workspace_outputs.total} workspaces. Only the first 10 workspaces are displayed in the printed table below:"""
            ).lstrip()
            tips = dedent(
                """
            To access your personal workspace, use \033[1mconnection\033[0m.my_workspace
            To access a specific workspace, use \033[1mconnection\033[0m.workspace(Workspace ID)"""
            ).lstrip()
            link = dedent(
                f"""
            For quick access to the list of workspaces in the Vectice web app, visit:
            {self._client.auth.api_base_url}/workspaces"""
            ).lstrip()
            temp_print(description)
            temp_print(table=rich_table)
            temp_print(tips)
            temp_print(link)

        return workspace_list

    @staticmethod
    def _get_host(config: str | None) -> str:
        try:
            return Connection._get_config_item("VECTICE_HOST", config)
        except ValueError:
            _logger.debug(f"No VECTICE_HOST provided. Using default host {DEFAULT_HOST}")
            return DEFAULT_HOST

    @staticmethod
    def _get_api_token(host: str, config: str | None) -> str:
        try:
            return Connection._get_config_item("VECTICE_API_TOKEN", config)
        except ValueError as error:
            raise ValueError(
                f"You must provide the api_token. You can generate them by going to the page {host}/account/api-keys"
            ) from error

    @staticmethod
    def _get_config_workspace(config: str | None) -> str | None:
        try:
            return Connection._get_config_item("WORKSPACE", config)
        except ValueError:
            return None

    @staticmethod
    def _get_config_project(config: str | None) -> str | None:
        try:
            return str(Connection._get_config_item("PROJECT", config))
        except ValueError:
            return None

    @staticmethod
    def _get_config_item(item_name: str, config_path: str | None) -> str:
        # search in provided config file
        with suppress(KeyError, SyntaxError, TypeError):
            config = Configuration(config_path)  # type: ignore[arg-type]
            if config[item_name]:
                _logger.debug(f"Found {item_name} in {config_path}")
                return config[item_name]
        # search in environment variables
        item = os.environ.get(item_name)
        if item:
            _logger.debug(f"Found {item_name} in environment variables.")
            return item
        # search in user configuration files
        for path in Connection.USER_FILES_PATH:
            with hide_logs("dotenv"):
                item = dotenv.get_key(path, item_name)
            if item:
                _logger.debug(f"Found {item_name} in {path}")
                return item
        raise ValueError(f"Could not find {item_name} in user configuration")

    def _log_workspace_or_project(
        self, workspace: str, project: str | None, user_name: str, host: str
    ) -> Workspace | Project:
        workspace_output: Workspace = self._get_workspace_from_str(workspace)
        if project:
            project_obj = self._log_project(workspace_output, project, user_name, host)
            self._workspace = project_obj.workspace
            _logger.debug(
                f"Successfully authenticated. You'll be working on Project: {project_obj.name!r}, part of Workspace: {project_obj.workspace.name!r}"
            )
            return project_obj

        workspace_obj = self._log_workspace(workspace_output, user_name, host)
        self._workspace = workspace_obj
        _logger.debug(f"Successfully authenticated. Your current Workspace: {workspace_output.name!r}")
        return workspace_obj

    def _log_workspace(self, workspace_output: Workspace, user_name: str, host: str) -> Workspace:
        _logger.info(
            CONNECTION_WORKSPACE_LOGGING.format(
                user=user_name, workspace_name=workspace_output.name, url=host, workspace_id=workspace_output.id
            )
        )
        return workspace_output

    def _log_project(self, workspace_output: Workspace, project: str, user_name: str, host: str) -> Project:
        project_output = self._get_project_from_str(project, workspace_output.id)

        _logger.info(
            CONNECTION_PROJECT_LOGGING.format(
                user=user_name,
                project_name=project_output.name,
                url=host,
                workspace_id=workspace_output.id,
                project_id=project_output.id,
            )
        )
        return project_output

    def _get_workspace_from_str(self, workspace: str) -> Workspace:
        return self._build_workspace_from_output(self._client.get_workspace(workspace))

    def _get_project_from_str(self, project: str, workspace: str | None = None) -> Project:
        return self._build_project_from_output(self._client.get_project(project, workspace))
