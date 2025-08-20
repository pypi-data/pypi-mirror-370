from __future__ import annotations

import difflib
import inspect
import logging
import os
from functools import reduce
from io import IOBase
from textwrap import dedent
from typing import TYPE_CHECKING, Any, ClassVar

from pandas import DataFrame
from PIL.Image import Image
from rich.table import Table as RichTable

from vectice.api.http_error_handlers import VecticeException
from vectice.api.json.iteration import (
    IterationOutput,
    IterationStatus,
    IterationUpdateInput,
)
from vectice.models.representation.attachment import Attachment
from vectice.models.validation import ValidationModel
from vectice.services.iteration_service import IterationService
from vectice.utils.common_utils import (
    check_read_only,
    ensure_correct_project_id_from_representation_objs,
    temp_print,
    wait_for_path,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe
from vectice.utils.instance_helper import is_image_or_file
from vectice.utils.last_assets import (
    assign_asset_version_logging,
    comment_or_image_logging,
    register_dataset_logging,
    register_model_logging,
    table_logging,
)
from vectice.utils.logging_utils import get_iteration_status

if TYPE_CHECKING:
    from vectice import Connection
    from vectice.api import Client
    from vectice.models import Phase, Project, Workspace
    from vectice.models.dataset import Dataset
    from vectice.models.model import Model
    from vectice.models.representation.dataset_representation import DatasetRepresentation
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.iteration_asset_representation import IterationAssetRepresentation
    from vectice.models.representation.model_representation import ModelRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation
    from vectice.models.table import Table

    TAssetType = ModelRepresentation | ModelVersionRepresentation | DatasetRepresentation | DatasetVersionRepresentation

_logger = logging.getLogger(__name__)


class Iteration:
    """Represents a Vectice iteration.

    An iteration is a recurring work cycle within a phase, primarily used for logging assets (models, datasets, graphs and notes)
    to document your work and maintain transparency throughout an AI project.

    By organizing work into iterations, you can share your key assets, make informed decisions based on previous work, and automatically track and document your progress.

    NOTE: **Each iteration may include sections for organizing assets together, contributing to a more structured narrative to share your work in the way you want.**

    Typical usage example:

    ```python
    # Create a new iteration within a phase
    iteration = phase.create_iteration()

    # Log a dataset to the iteration
    iteration.log(my_dataset)

    # Log a model to the iteration with optional section assignment
    iteration.log(my_model, section="Modeling")
    ```

    NOTE: **You can create sections dynamically using the API.**

    To create a new iteration:

    ```python
    iteration = phase.create_iteration()
    ```
    """

    __slots__: ClassVar[list[str]] = [
        "__dict__",
        "_client",
        "_description",
        "_id",
        "_index",
        "_name",
        "_phase",
        "_service",
        "_status",
        "_steps",
    ]

    def __init__(
        self,
        output: IterationOutput,
        phase: Phase,
        client: Client,
    ):
        self.__dict__ = {}
        self._id = output.id
        self._index = output.index
        self._name = output.name
        self._description = output.description
        self._phase = phase
        self._status = output.status
        self._client = client
        self._service = IterationService(self, self._client)

    def __repr__(self) -> str:
        return f"Iteration (name={self._name}, id={self._id}, status={get_iteration_status(self._status)})"

    def __eq__(self, other: object):
        if not isinstance(other, Iteration):
            return NotImplemented
        return self.id == other.id

    @property
    def id(self) -> str:
        """The iteration's identifier.

        Returns:
            The iteration's identifier.
        """
        return self._id

    @id.setter
    def id(self, iteration_id: str):
        """Set the iteration's identifier.

        Parameters:
            iteration_id: The identifier.
        """
        check_read_only(self)
        self._id = iteration_id

    @property
    def index(self) -> int:
        """The iteration's index.

        Returns:
            The iteration's index.
        """
        return self._index

    @property
    def name(self) -> str:
        """The iteration's name.

        Returns:
            The iteration's name.
        """
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def description(self) -> str | None:
        """The iteration's description.

        Returns:
            The iteration's description.
        """
        return self._description

    @description.setter
    def description(self, description: str | None):
        self._description = description

    @property
    def status(self) -> str:
        """The iteration's status.

        Returns:
            The iteration's status.
        """
        return get_iteration_status(self._status)

    @property
    def completed(self) -> bool:
        """Whether this iteration is completed.

        Returns:
            Whether the iteration is completed.
        """
        return self._status is IterationStatus.Completed

    @property
    def properties(self) -> dict[str, int | str]:
        """The iteration's identifier, index and name.

        Returns:
            A dictionary containing the `id`, `index` and `name` items.
        """
        return {"id": self.id, "index": self.index, "name": self.name}

    def print_phase_requirements(self) -> None:
        """Prints a list of phase requirements in a tabular format, limited to the first 10 requirements. A link is provided to view the remaining requirements.

        Returns:
            None
        """
        paged_requirements = self._client.list_step_definitions(self.phase.id)

        rich_table = RichTable(expand=True, show_edge=False)

        rich_table.add_column("Title", justify="left", no_wrap=True, min_width=5, max_width=40)
        rich_table.add_column("Description", justify="left", no_wrap=False, min_width=5, max_width=35)

        for requirement in paged_requirements.list:
            description = requirement.description.strip() if requirement.description else None
            rich_table.add_row(requirement.name, description)

        description = f"""There are {paged_requirements.total} requirements in the phase {self.phase.name!r} and a maximum of 10 requirements are displayed in the table below:"""
        link = dedent(
            f"""
                For quick access to the phase requirements in the Vectice web app, visit:
                {self._client.auth.api_base_url}/phase/{self.phase.id}/requirements
            """
        ).lstrip()

        temp_print(description)
        temp_print(table=rich_table)
        temp_print(link)

    def print_sections(self) -> None:
        """Prints a list of sections belonging to the iteration in a tabular format, limited to the first 10 sections. A link is provided to view the remaining sections.

        Returns:
            None
        """
        iteration_output = self._client.list_sections(self.id)

        rich_table = RichTable(expand=True, show_edge=False)

        rich_table.add_column("Name", justify="left", no_wrap=True, min_width=5, max_width=40)
        rich_table.add_column("Assets (count)", justify="left", no_wrap=True, min_width=5, max_width=15)

        if iteration_output.artifacts_count > 0:
            rich_table.add_row("None ('Assets without section')", str(iteration_output.artifacts_count))

        for section in iteration_output.sections.list:
            rich_table.add_row(section.name, str(section.artifacts_count))

        description = f"""There are {iteration_output.sections.total} sections in the iteration {self.name!r} and a maximum of 10 sections are displayed in the table below:"""
        link = dedent(
            f"""
                >> To log an asset to a specific section, use iteration.log()
                For quick access to the iteration in the Vectice web app, visit:
                {self._client.auth.api_base_url}/browse/iteration/{self.id}
            """
        ).lstrip()

        temp_print(description)
        temp_print(table=rich_table)
        temp_print(link)

    def cancel(self) -> None:
        """Cancel the iteration."""
        iteration_input = IterationUpdateInput(status=IterationStatus.Abandoned.name)
        self._client.update_iteration(self.id, iteration_input)
        self._status = IterationStatus.Abandoned
        _logger.info(f"Iteration {self.name} cancelled.")

    def complete(self) -> None:
        """Mark the iteration as completed."""
        iteration_input = IterationUpdateInput(status=IterationStatus.Completed.name)
        self._client.update_iteration(self.id, iteration_input)
        self._status = IterationStatus.Completed
        logging_output = dedent(
            f"""
                        Iteration {self.name!r} completed.

                        For quick access to the Iteration in the Vectice web app, visit:
                        {self._client.auth.api_base_url}/browse/iteration/{self.id}"""
        ).lstrip()
        _logger.info(logging_output)

    def delete(self) -> None:
        """Permanently deletes the iteration."""
        self._client.delete_iteration(self.id)
        _logger.info(f"Iteration {self.name} was deleted.")

    @property
    def connection(self) -> Connection:
        """The connection to which this iteration belongs.

        Returns:
            The connection to which this iteration belongs.
        """
        return self._phase.connection

    @property
    def workspace(self) -> Workspace:
        """The workspace to which this iteration belongs.

        Returns:
            The workspace to which this iteration belongs.
        """
        return self._phase.workspace

    @property
    def project(self) -> Project:
        """The project to which this iteration belongs.

        Returns:
            The project to which this iteration belongs.
        """
        return self._phase.project

    @property
    def phase(self) -> Phase:
        """The phase to which this iteration belongs.

        Returns:
            The phase to which this iteration belongs.
        """
        return self._phase

    def delete_assets_in_section(self, section: str) -> None:
        """Delete assets within a specified section of the iteration. This action is irreversible, and the deleted assets cannot be recovered.

        ```python
        iteration.delete_assets_in_section(section="Collect Initial Data")
        ```

        Parameters:
            section: The iteration's section where the assets are displayed in the Vectice App.
        """
        self._client.remove_iteration_assets(iteration_id=self._id, section=section)
        _logger.info(f"All assets in section {section!r} are deleted.")

    def delete_assets_without_a_section(self) -> None:
        """Delete assets without a section of the iteration. This action is irreversible, and the deleted assets cannot be recovered.

        ```python
        iteration.delete_assets_without_a_section()
        ```
        """
        self._client.remove_iteration_assets(iteration_id=self._id)
        _logger.info("All assets without a section are deleted.")

    def delete_assets_from_iteration(self) -> None:
        """Delete all assets from the iteration. This action is irreversible, and the deleted assets cannot be recovered.

        ```python
        iteration.delete_assets_from_iteration()
        ```
        """
        self._client.remove_iteration_assets(iteration_id=self._id, all=True)
        _logger.info(f"All assets from iteration {self.name!r} are deleted.")

    def delete_asset(self, asset: str) -> None:
        """Delete an asset from the iteration. This action is irreversible, and the deleted assets cannot be recovered.

            asset: The asset Vectice ID, filename or table name.

        ```python
        iteration.delete_asset(asset="MDV-XXXX")
        ```
        """
        asset_id = next(
            (
                artifact._artifact_id  # type: ignore[reportPrivateUsage]
                for artifact in self.list_assets()
                if artifact.asset_id == asset or artifact.asset_name == asset
            ),
            None,
        )
        if asset_id is None:
            raise VecticeException(f"The asset '{asset}' is not valid.")
        self._client.remove_assets_from_iteration(iteration_id=self._id, artifacts_id_list=[int(asset_id)])
        _logger.info(f"Asset '{asset}' from iteration {self.name!r} was deleted.")

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update the Iteration from the API.

            name: The new name of the iteration.
            description: The new description of the iteration.

        Returns:
            None
        """
        self._service.update(name, description)

    def _log_fact_sheet(self, modeva_asset: dict, section: str | None = None):
        self._client.assert_feature_flag_or_raise("modeva-api-integration")  # type: ignore[reportPrivateUsage]

        from vectice import Dataset, DatasetType, NoResource
        from vectice.models.resource.metadata.db_metadata import TableType

        if section is None:
            section = "validation assets"
        dataframe = modeva_asset.get("dataset")
        if dataframe is not None:
            no_resource_dataset = Dataset(
                type=DatasetType.UNKNOWN,
                resource=NoResource(
                    dataframes=dataframe,
                    origin="DATAFRAME",
                    type=TableType.UNKNOWN,
                    capture_schema_only=False,
                ),
            )
            self._log_dataset(no_resource_dataset, section)
        if modeva_asset.get("models"):
            from vectice.models.model import Model

            models = modeva_asset["models"]
            for model in models:
                vect_model = Model(
                    library=model.get("library"),
                    technique=model.get("technique"),
                    properties=model.get("properties"),
                    predictor=model.get("model"),
                )
                self._log_model(vect_model, section)

        if modeva_asset.get("validation_results"):
            from vectice.autolog.autolog_asset_factory import AssetFactory

            validation_results = modeva_asset["validation_results"]
            for validation in validation_results:
                validation_asset = AssetFactory.get_asset_service("none", validation, {}, self.id).get_asset()
                if validation_asset:
                    self._log_validation_result(validation_asset)

    def _get_modeva_docs(self, key: str) -> str | None:
        from modeva import (  # type: ignore[reportMissingImports]
            DataSet,  # type: ignore[reportMissingImports]
            FactSheet,  # type: ignore[reportMissingImports]
        )

        methods_docstrings = {}
        combined_dict = {**DataSet.__dict__, **FactSheet.__dict__}

        for name, member in combined_dict.items():
            try:
                methods_docstrings[name] = inspect.getdoc(member.__func__).split("\n")[0]  # type: ignore[reportOptionalMemberAccess]
            except Exception:
                pass
            try:
                methods_docstrings[name] = inspect.getdoc(member).split("\n")[0]  # type: ignore[reportOptionalMemberAccess]
            except Exception:
                pass

        test_info = methods_docstrings.get(key)
        if test_info is None:
            # closest matching key, fuzzy matching.
            match = difflib.get_close_matches(key, ["eda_1d"], n=1)
            closest_key = match[0] if match else None
            return methods_docstrings.get(closest_key)

        return test_info

    def _log_validation_result(self, modeva_asset: dict, section: str | None = None):
        self._client.assert_feature_flag_or_raise("modeva-api-integration")  # type: ignore[reportPrivateUsage]

        from vectice import Table

        asset = modeva_asset["asset"]

        if section is None:
            section = asset.key

        test_info = self._get_modeva_docs(asset.key)

        if test_info:
            self._log_comment(test_info, section)

        table_prefix = asset.key
        dataframes = modeva_asset.get("table")
        plots = modeva_asset.get("plot")
        if dataframes:
            for index, dataframe in enumerate(dataframes):
                try:
                    # get the multindex as a suffix
                    suffix = dataframe.columns.levels[0][index]
                    # drop the main header level
                    dataframe = dataframe.droplevel(level=0, axis=1)
                    table_name = f"{table_prefix}_{suffix}"
                except Exception:
                    table_name = table_prefix
                table = Table(name=table_name, dataframe=dataframe)
                self._log_table(table, section)
        if plots:
            for plot in plots:
                try:
                    # we need to wait for modeva to save the plot
                    wait_for_path(plot, timeout=20, interval=0.5)
                except TimeoutError as e:
                    print(e)
                self._log_image_or_file(plot, section)

    def _log_scan_report(self, giskard_asset: dict, section: str | None = None):
        self._client.assert_feature_flag_or_raise("giskard-api-integration")

        if section is None:
            section = "Scan Results"

        if giskard_asset.get("results_dataset"):
            dataset = giskard_asset["results_dataset"]
            self._log_dataset(dataset, section)

        if giskard_asset.get("issues"):
            issues = giskard_asset["issues"]
            curr_section = None
            for issue in issues:
                section = issue["section"]
                comment = issue["section_description"]
                level_info = issue["level"]
                table = issue["table"]
                if curr_section is None or (curr_section is not None and curr_section != section):
                    self._log_comment(comment, section)
                    curr_section = section
                self._log_comment(level_info, section)
                self._log_table(table, section)

    def _get_giskard_docs(self, key: str) -> str | None:
        from giskard.rag.report import RAGReport  # type: ignore[reportMissingImports]

        methods_docstrings = {}
        combined_dict = {**RAGReport.__dict__}

        for name, member in combined_dict.items():

            try:
                methods_docstrings[name] = inspect.getdoc(member.__func__).split("\n")[0]  # type: ignore[reportOptionalMemberAccess]
            except Exception:
                pass
            try:
                methods_docstrings[name] = inspect.getdoc(member).split("\n")[0]  # type: ignore[reportOptionalMemberAccess]
            except Exception:
                pass

        test_info = methods_docstrings.get(key)
        return test_info

    def _log_rag_report(self, giskard_asset: dict, section: str | None = None):
        self._client.assert_feature_flag_or_raise("giskard-api-integration")

        if section is None:
            section = "Rag Report"
        if giskard_asset.get("recommendation"):
            recommendation = giskard_asset["recommendation"]
            self._log_comment(recommendation, section)
        if giskard_asset.get("report_dataset"):
            dataset = giskard_asset["report_dataset"]
            self._log_dataset(dataset, section)
        tables = giskard_asset.get("tables")
        if tables is not None:
            for table in tables:
                description = self._get_giskard_docs(table.name)
                if description:
                    self._log_comment(description, section)
                self._log_table(table, section)

    def _log_test_suite_result(self, giskard_asset: dict, section: str | None = None):
        self._client.assert_feature_flag_or_raise("giskard-api-integration")

        attachment = giskard_asset.get("attachment")
        suite_name = giskard_asset.get("suite_name")
        if section is None:
            section = suite_name
        if attachment is not None:
            self._log_image_or_file(attachment, section)

    def _log_qa_test(self, giskard_asset: dict, section: str | None = None):
        from vectice import Dataset, DatasetType, FileResource

        self._client.assert_feature_flag_or_raise("giskard-api-integration")

        if section is None:
            section = "QA Test Set"
        dataframe = giskard_asset.get("dataframe")
        table = giskard_asset.get("table")
        path = giskard_asset.get("csv")
        if dataframe is not None:
            resource = FileResource(path, dataframes=dataframe, capture_schema_only=False)  # type: ignore[reportArgumentType]
            resource_dataset = Dataset(type=DatasetType.UNKNOWN, resource=resource, attachments=[table, path])  # type: ignore[reportArgumentType]
            self._log_dataset(resource_dataset, section)

    def log(self, asset: Any, section: str | None = None) -> None:
        """Log an asset to an iteration. Assets can be organized into sections for improved clarity within the iteration.

        ```python
        from vectice import Model
        my_model = Model(name="my_model")
        iteration.log(my_model)
        iteration.log("my note")
        ```

        Parameters:
            asset: The asset to log to an iteration. Assets can include notes, images, Vectice datasets, or Vectice models.
            section (Optional): The iteration's section where the asset will be displayed in the Vectice App. Assets without sections are logged in the iteration itself.

        """
        # TODO: cyclic imports
        from importlib.util import find_spec

        from vectice.autolog.autolog_asset_factory import AssetFactory
        from vectice.models.dataset import Dataset
        from vectice.models.model import Model
        from vectice.models.representation.dataset_representation import DatasetRepresentation
        from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
        from vectice.models.representation.model_representation import ModelRepresentation
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation
        from vectice.models.table import Table

        is_modeva = find_spec("modeva") is not None
        is_giskard = find_spec("giskard") is not None

        ensure_correct_project_id_from_representation_objs(self.project.id, asset)

        if section:
            section = section.strip()

        if section is not None and len(section) > 60:
            raise VecticeException("section: name must be shorter than or equal to 60 characters")

        giskard_asset = None
        if is_giskard:
            from giskard.rag import QATestset  # type: ignore[reportMissingImports]
            from giskard.rag.report import RAGReport  # type: ignore[reportMissingImports]
            from giskard.scanner.report import ScanReport  # type: ignore[reportMissingImports]

            if isinstance(asset, (QATestset, RAGReport, ScanReport)):
                giskard_asset = AssetFactory.get_asset_service("none", asset, {}, self.id).get_asset()
                if giskard_asset and giskard_asset["type"] == "scan":
                    self._log_scan_report(giskard_asset, section)
                if giskard_asset and giskard_asset["type"] == "rag":
                    self._log_rag_report(giskard_asset, section)
                if giskard_asset and giskard_asset["type"] == "qatest":
                    self._log_qa_test(giskard_asset, section)
                return None

        modeva_asset = None
        if is_modeva:
            from modeva import FactSheet  # type: ignore[reportMissingImports]
            from modeva.utils.results import ValidationResult  # type: ignore[reportMissingImports]

            try:
                if isinstance(asset, (FactSheet, ValidationResult)):
                    modeva_asset = AssetFactory.get_asset_service("none", asset, {}, self.id).get_asset()
                # if modeva_asset and (modeva_asset.get("models") or "dataframe" in modeva_asset):
                #   self._log_fact_sheet(modeva_asset, section)
                if modeva_asset and "table" in modeva_asset:
                    self._log_validation_result(modeva_asset, section)
            except Exception:
                pass

        if modeva_asset or giskard_asset:
            return

        elif is_image_or_file(asset):
            self._log_image_or_file(asset, section)

        elif isinstance(asset, (int, float, str)):
            self._log_comment(asset, section)

        elif isinstance(asset, Table):
            self._log_table(asset, section)

        elif isinstance(
            asset,
            (ModelRepresentation, ModelVersionRepresentation, DatasetRepresentation, DatasetVersionRepresentation),
        ):
            self._assign_version_representation(asset, section)

        elif isinstance(asset, Model):
            if asset.predictor:
                self._assign_model_predictor_metadata(asset)
            self._log_model(asset, section)

        elif isinstance(asset, Dataset):
            self._log_dataset(asset, section)
        elif isinstance(asset, ValidationModel):
            self._log_validation_model(asset, section)
        else:
            raise TypeError(f"Expected Image, Comment, Table, Dataset or a Model, got {type(asset)}")

    def _log_image_or_file(self, asset: str | IOBase | Image, section: str | None = None):
        filename = self._service.log_image_or_file(asset, section)
        comment_or_image_logging(self, _logger, section, filename)

    def _log_comment(self, asset: int | float | str, section: str | None = None):
        self._service.log_comment(asset, section)
        comment_or_image_logging(self, _logger, section)

    def _log_table(self, asset: Table, section: str | None = None):
        self._service.log_table(asset, section)
        table_logging(self, asset, _logger, section)

    def _assign_version_representation(
        self,
        asset: TAssetType,
        section: str | None = None,
    ):
        _, already_assigned = self._service.assign_version_representation(asset, section)
        assign_asset_version_logging(
            iteration=self,
            value=asset,
            _logger=_logger,
            already_assigned=already_assigned,
            section=section,
        )

    def _log_model(self, asset: Model, section: str | None = None):
        model_data, attachments_output, success_pickle = self._service.log_model(asset, section)

        register_model_logging(self, model_data, asset, attachments_output, success_pickle, _logger, section)

    def _log_dataset(self, asset: Dataset, section: str | None = None):
        dataset_output, attachments_output = self._service.log_dataset(asset, section)
        register_dataset_logging(self, dataset_output, asset, attachments_output, _logger, section)

    def _log_validation_model(self, asset: ValidationModel, section: str | None = None):
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        self._client.assert_feature_flag_or_raise("validation-library")

        validated = asset.execute_test()
        metrics = validated.get("metrics") if len(validated.get("metrics")) > 0 else None
        properties = validated.get("properties") if len(validated.get("properties")) > 0 else None
        attachments = validated.get("attachments") if len(validated.get("attachments")) > 0 else None

        if asset.asset:
            mdv = ModelVersionRepresentation(output=self._client.get_model_version(asset.asset), client=self._client)
            mdv.update(metrics=metrics, properties=properties, attachments=attachments)
            self._assign_version_representation(mdv)
        else:
            if attachments is not None:
                for attachment in attachments:
                    self._log_image_or_file(attachment, section)

        tables = validated.get("table")
        if tables is not None:
            for table in tables:
                self._log_table(table, section)

    def _assign_model_predictor_metadata(self, asset: Model) -> None:
        from vectice.autolog.autolog_asset_factory import AssetFactory

        asset_information = AssetFactory.get_asset_service(
            "key", asset.predictor, {"cell": None, "variables": None}, self.id
        ).get_asset()
        if asset_information and asset_information["model"]:
            model = asset_information["model"]
            technique, params, library = (
                model.technique,
                model.properties,
                model.library,
            )
            if technique and asset.technique is None:
                asset.technique = technique
            if params and asset.properties is None:
                # disable update model properties warning
                logger = logging.getLogger("vectice.models.model")
                logger.disabled = True

                asset.properties = params

                logger.disabled = False
            if library and asset.library is None:
                asset.library = library

    def list_assets(self) -> list[IterationAssetRepresentation]:
        """Retrieves a list of assets associated with the iteration.

        Returns:
            list[IterationAssetRepresentation]: A list of IterationAssetRepresentation objects representing the assets
                associated with the iteration.
        """
        from vectice.models.representation.iteration_asset_representation import IterationAssetRepresentation

        return reduce(
            lambda acc, asset: [*acc, IterationAssetRepresentation(asset, self._client)],
            self._client.list_iteration_assets(self.id).list,
            [],
        )

    def list_attachments(self) -> list[Attachment]:
        """Lists all the attachments (tables, files, pickle...) of the Iteration.

        Returns:
            The attachments list.
        """
        return self._client.list_attachments(self)

    def download_attachments(self, attachments: list[str] | str | None = None, output_dir: str | None = None) -> None:
        """Downloads a list of attachments associated with the current iteration.

        Parameters:
            attachments: A list of attachment file names or a single attachment file name
                                                  to be downloaded. If None, all attachments will be downloaded.
            output_dir: The directory path where the attachments will be saved.
                                      If None, the current working directory is used.

        Returns:
            None
        """
        if output_dir is None:
            output_dir = os.getcwd()
        os.makedirs(output_dir, exist_ok=True)

        if attachments is None:
            attachments = list(map(lambda attach: attach.name, self.list_attachments()))

        if isinstance(attachments, str):
            attachments = [attachments]

        for attachment in attachments:
            self._client.download_attachment(self, attachment, output_dir)

    def get_table(self, table: str) -> DataFrame:
        """Retrieves a table associated with the current iteration.

        Parameters:
            table: The name of the table.

        Returns:
            The data from the specified table as a DataFrame.
        """
        return repr_list_as_pd_dataframe(self._client.get_version_table(self, table))
