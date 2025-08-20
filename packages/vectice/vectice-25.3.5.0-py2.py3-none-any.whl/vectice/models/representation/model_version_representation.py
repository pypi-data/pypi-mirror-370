from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

from vectice.api.json.model_version import ModelVersionStatus
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput, ModelVersionUpdateInput
from vectice.models.attachment import TAttachment
from vectice.models.attachment_container import AttachmentContainer
from vectice.models.metric import Metric
from vectice.models.property import Property
from vectice.models.representation.attachment import Attachment
from vectice.models.representation.issue_representation import IssueRepresentation
from vectice.models.representation.model_representation import ModelRepresentation
from vectice.models.representation.report_representation import ReportRepresentation
from vectice.utils.api_utils import DEFAULT_MAX_SIZE, DEFAULT_NUMBER_OF_ITEMS
from vectice.utils.common_utils import (
    convert_list_keyvalue_to_dict,
    format_attachments,
    format_metrics,
    format_properties,
    repr_class,
    strip_dict_list,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.api.client import Client
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation


class ModelVersionRepresentation:
    """Represents the metadata of a Vectice model version.

    A Model Version Representation shows information about a specific version of a model from the Vectice app.
    It makes it easier to get and read this information through the API.

    NOTE: **Hint**
        A model version ID starts with 'MDV-XXX'. Retrieve the ID in the Vectice App, then use the ID with the following methods to get the model version:
        ```connect.model_version('MDV-XXX')``` or ```connect.browse('MDV-XXX')```
        (see [Connection page](https://api-docs.vectice.com/reference/vectice/connection/#vectice.Connection.model_version)).

    Attributes:
        id (str): The unique identifier of the model version.
        project_id (str): The identifier of the project to which the model version belongs.
        name (str): The name of the model version. For model versions it corresponds to the version number.
        status (str): The status of the model version (EXPERIMENTATION, STAGING, PRODUCTION, or RETIRED).
        risk (str): The risk status of the model version (HIGH, MEDIUM, LOW, or UNDEFINED).
        approval (str): The approval status of the model version (ToValidate, InValidation, Validated, Approved, or Rejected).
        description (str): The description of the model version.
        technique (str): The technique used by the model version.
        library (str): The library used by the model version.
        inventory_id (str | None): The model version inventory id.
        iteration_origin (str | None): The iteration in which this model version was created.
        phase_origin (str | None): The phase in which this model version was created.
        metrics (List[Dict[str, Any]]): The metrics associated with the model version.
        properties (List[Dict[str, Any]]): The properties associated with the model version.
        model_representation (ModelRepresentation): Holds informations about the source model linked to the model version, where all versions are grouped together.
        creator (Dict[str, str]): Creator of the model version.
    """

    def __init__(
        self, output: ModelVersionRepresentationOutput, client: Client, model: ModelRepresentation | None = None
    ):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.is_starred = output.is_starred
        self.status = output.status
        self.risk = output.risk
        self.approval = output.approval
        self.description = output.description
        self.technique = output.technique
        self.library = output.library
        self.inventory_id = output.inventory_id
        self.iteration_origin = output.iteration_origin
        self.phase_origin = output.phase_origin
        self.metrics = output.metrics
        self.properties = strip_dict_list(output.properties)
        self.model_representation = model if model else ModelRepresentation(output.model, client)
        self.creator = output.creator

        self._client = client
        self._output = output

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the ModelVersionRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        flat_metrics = convert_list_keyvalue_to_dict(self.metrics)
        flat_properties = convert_list_keyvalue_to_dict(self.properties)

        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "is_starred": self.is_starred,
            "status": self.status,
            "risk": self.risk,
            "approval": self.approval,
            "description": self.description,
            "technique": self.technique,
            "library": self.library,
            "inventory_id": self.inventory_id,
            "metrics": flat_metrics,
            "properties": flat_properties,
            "iteration_origin": self.iteration_origin,
            "phase_origin": self.phase_origin,
            "model_representation": (self.model_representation.asdict() if self.model_representation else None),
            "creator": self.creator,
        }

    def list_attachments(self) -> list[Attachment]:
        """Lists all the attachments (tables, files, pickle...) of the ModelVersionRepresentation.

        Returns:
            The attachments list.
        """
        return self._client.list_attachments(self)

    def get_table(self, table: str) -> DataFrame:
        """Extracts the Vectice table in attachment of the model version representation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame representing the table of the model version.
        """
        return repr_list_as_pd_dataframe(self._client.get_version_table(self, table))

    def metrics_as_dataframe(self) -> DataFrame:
        """Transforms the metrics of the ModelVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the metrics of the model version.
        """
        return repr_list_as_pd_dataframe(self.metrics)  # change key name

    def properties_as_dataframe(self) -> DataFrame:
        """Transforms the properties of the ModelVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the properties of the model version.
        """
        return repr_list_as_pd_dataframe(self.properties)  # change key name

    def download_attachments(self, attachments: list[str] | str | None = None, output_dir: str | None = None) -> None:
        """Downloads attachments of this version.

        Parameters:
            attachments: Specific attachments to download, if None then all the version attachments will be downloaded.
            output_dir: Destination for the attachments to be downloaded to. If None then attachments will be downloaded to the current directory.

        Returns:
            None.
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

    def list_lineage_inputs(self) -> list[DatasetVersionRepresentation]:
        """Retrieves all the lineage inputs of the current model version.

        Returns:
            The list of dataset version used as input of the current model version.
        """
        from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation

        return list(
            map(
                lambda output: DatasetVersionRepresentation(output, self._client),
                self._client.get_lineage_inputs(self.id, "mdv"),
            )
        )

    def list_reports(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS) -> list[ReportRepresentation]:
        """Retrieves a list of issue representations associated with the current model version.
        See here: https://api-docs.vectice.com/reference/vectice/representation/issue/
        Parameters:
            number_of_items: The number of reports to retrieve. Defaults to 30.

        Returns:
            A list of `ReportRepresentation` instances corresponding to the reports in the current model version.
        """
        self._client.assert_feature_flag_or_raise("list-reports")

        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 reports will be retrieved. For additional reports, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        outputs = self._client.get_reports(self.id, "mdv", number_of_items)
        reps = [ReportRepresentation(report, self._client) for report in outputs.list]
        return reps

    def list_issues(self, number_of_items: int = DEFAULT_NUMBER_OF_ITEMS) -> list[IssueRepresentation]:
        """Retrieves a list of issue representations associated with the current model version.
        See here: https://api-docs.vectice.com/reference/vectice/representation/issue/

        Parameters:
            number_of_items: The number of issues to retrieve. Defaults to 30.

        Returns:
            A list of `IssueRepresentation` instances corresponding to the issues in the current model version.
        """
        if number_of_items > DEFAULT_MAX_SIZE:
            _logger.warning(
                "Only the first 100 issues will be retrieved. For additional issues, please contact your sales representative or email support@vectice.com"
            )
            number_of_items = DEFAULT_MAX_SIZE
        outputs = self._client.get_issues(self.id, "mdv", number_of_items)
        reps = [IssueRepresentation(issue, self._client) for issue in outputs.list]
        return reps

    def get_approval_history(self) -> dict[str, datetime | None]:
        """Retrieves approval history of the current model version.

        Returns:
            A dictionary with last updated dates for each model version approval status.
        """
        self._client.assert_feature_flag_or_raise("model-version-approval-history")

        return self._client.get_model_version_approval_history(self.id)

    def update(
        self,
        status: str | None = None,
        metrics: dict[str, int | float] | list[Metric] | Metric | None = None,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: TAttachment | None = None,
    ) -> None:
        """Update the Model Version from the API.

        Parameters:
            status: The new status of the model. Accepted values are EXPERIMENTATION, STAGING, PRODUCTION and RETIRED.
            properties: The new properties of the model.
            metrics: The new metrics of the model.
            attachments: The new attachments of the model.

        Returns:
            None
        """
        if status is not None:
            self._update_status(status)

        if attachments is not None:
            self._update_attachments(attachments)

        if metrics is not None:
            self._upsert_metrics(metrics)

        if properties is not None:
            self._upsert_properties(properties)

    def _update_status(self, status: str):
        try:
            status_enum = ModelVersionStatus(status.strip().upper())
        except ValueError as err:
            accepted_statuses = ", ".join([f"{status_enum.value!r}" for status_enum in ModelVersionStatus])
            raise ValueError(f"'{status}' is an invalid value. Please use [{accepted_statuses}].") from err

        model_input = ModelVersionUpdateInput(status=status_enum.value)
        self._client.update_model(self.id, model_input)
        old_status = self.status
        self.status = status_enum.value
        _logger.info(f"Model version {self.id!r} transitioned from {old_status!r} to {self.status!r}.")

    def _upsert_properties(self, properties: dict[str, str | int] | list[Property] | Property):
        clean_properties = list(map(lambda property: property.key_val_dict(), format_properties(properties)))
        new_properties = self._client.upsert_properties("modelVersion", self.id, clean_properties)
        self.properties = strip_dict_list(new_properties)
        _logger.info(f"Model version {self.id!r} properties successfully updated.")

    def _upsert_metrics(self, metrics: dict[str, int | float] | list[Metric] | Metric):
        clean_metrics = list(map(lambda metric: metric.key_val_dict(), format_metrics(metrics)))
        self.metrics = self._client.upsert_metrics("modelVersion", self.id, clean_metrics)
        _logger.info(f"Model version {self.id!r} metrics successfully updated.")

    def _update_attachments(self, attachments: TAttachment):
        container = AttachmentContainer(self._output, self._client)
        container.upsert_attachments(format_attachments(attachments))
        _logger.info(f"Model version {self.id!r} attachments successfully updated.")
