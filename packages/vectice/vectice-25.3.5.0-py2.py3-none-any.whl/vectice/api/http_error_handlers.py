from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, NoReturn

from vectice.utils.vectice_ids_regex import ITERATION_VID_REG, PHASE_VID_REG, PROJECT_VID_REG, WORKSPACE_VID_REG

if TYPE_CHECKING:
    from gql.transport.exceptions import TransportQueryError

    from vectice.api.http_error import HttpError

BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE = "Bad or missing credentials"


class InvalidIdError(ValueError):
    """When an incorrect value type is passed at the client level."""

    def __init__(self, reference_type: str, value: Any) -> None:
        valid_id = "a valid id"
        wsp = "WSP-[int]"
        prj = "PRJ-[int]"
        pha = "PHA-[int]"
        itr = "ITR-[int]"
        dts = "DTS-[int]"
        dsv = "DTV-[int]"
        mod = "MDL-[int]"
        mdv = "MDV-[int]"
        if reference_type == "workspace":
            valid_id = wsp
        elif reference_type == "project":
            valid_id = prj
        elif reference_type == "phase":
            valid_id = pha
        elif reference_type == "iteration":
            valid_id = itr
        elif reference_type == "dataset":
            valid_id = dts
        elif reference_type == "dataset_version":
            valid_id = dsv
        elif reference_type == "model":
            valid_id = mod
        elif reference_type == "model_version":
            valid_id = mdv
        elif reference_type == "asset":
            refs = {", ".join([wsp, prj, pha, itr, dts, dsv, mod, mdv])}
            valid_id = f"one of ({refs})"

        super().__init__(
            f"The {reference_type} reference is invalid. Please check the provided value. "
            + f"It should be {valid_id} "
            + f"Provided value is {value}"
        )


class InvalidReferenceError(ValueError):
    """When an incorrect value type is passed at the client level."""

    def __init__(self, reference_type: str, value: Any) -> None:
        super().__init__(
            f"The {reference_type} reference is invalid."
            + "Please check the provided value as it should be a string or a number."
            + f"Provided value is {value} ({type(value)})"
        )


class MissingReferenceError(ValueError):
    """When a value is missing at the client level."""

    def __init__(self, reference_type: str, parent_reference_type: str | None = None) -> None:
        if parent_reference_type is not None:
            super().__init__(f"The {parent_reference_type} reference is required if the {reference_type} name is given")
        else:
            super().__init__(f"The {reference_type} reference is required")


class ClientErrorHandler:
    def _graphql_error_formatter(self, error: TransportQueryError) -> Exception:
        error_field = error.errors[0] if error.errors else {}
        error_message = "An unknown error occured, please contact support."
        if "extensions" in error_field and "exception" in error_field["extensions"]:
            exception = error_field["extensions"]["exception"]
            if "stacktrace" in exception:
                # try to format the message
                error_code = 500
                message = exception["stacktrace"]
                if message and len(message) >= 1 and isinstance(message[0], str):
                    message = message[0].split(":")
                    if len(message) > 1:
                        error_code = message[0]
                        error_message = message[1]
                raise VecticeException(f"{error_code}: {error_message}")
        elif "message" in error_field:
            error_message = error_field["message"]

        # just dump the stringified error
        raise VecticeException(repr(error_message))

    def handle_code(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        if e.code == 404:
            raise BadReferenceFactory.get_reference(reference_type, reference)
        elif e.code == 401:
            raise ConnectionRefusedError(BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE)
        elif e.code == 403:
            raise PermissionError(f"Missing permissions to access this {reference_type}")
        elif e.code == 412 and reference_type == "iteration":
            raise VecticeException(f"{reference_type}: {e.reason}")
        raise RuntimeError(f"Can not access {reference_type}: {e.reason}")

    def handle_get_http_error(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        self.handle_code(e, reference_type, reference)

    def handle_put_http_error(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        self.handle_code(e, reference_type, reference)

    def handle_delete_http_error(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        self.handle_code(e, reference_type, reference)

    def handle_post_http_error(self, e: HttpError, reference_type: str, action: str = "create") -> NoReturn:
        if e.code == 401:
            raise ConnectionRefusedError(BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE)
        elif e.code == 403:
            raise PermissionError(f"Missing permissions to access this {reference_type}")
        elif e.code == 400:
            raise RuntimeError(f"Can not {action} {reference_type}: {e.reason}")
        raise RuntimeError(f"Unexpected error: {e.reason}")

    def get_gql_error_info(self, error: TransportQueryError) -> tuple[int, str, str]:
        try:
            status_code = error.errors[0]["extensions"]["exception"]["status"]  # type: ignore[index]
            key = error.errors[0]["extensions"]["key"]  # type: ignore[index]
            message = error.errors[0]["message"]  # type: ignore[index]
        except KeyError:
            status_code = -1
            key = ""
            message = ""
        return status_code, key, message

    def handle_post_gql_error(self, error: TransportQueryError, reference_type: str, reference: str | int) -> NoReturn:
        status_code, key, message = self.get_gql_error_info(error)

        if status_code == 404:
            raise BadReferenceFactory.get_reference(reference_type, reference, key, message)
        elif status_code == 401:
            raise ConnectionRefusedError(BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE)
        elif status_code == 403:
            raise PermissionError(f"Missing permissions to access this {reference_type}")
        elif status_code == 400 or status_code == 412:
            raise BadRequestFactory.get_reference(reference_type, error)
        elif status_code == 409 and reference_type == "iteration":
            raise ArtifactVersionIdExistingError()
        raise self._graphql_error_formatter(error) from error


class BadRequestFactory:
    @classmethod
    def get_reference(cls, reference_type: str, error: TransportQueryError) -> Exception:
        message: str = "failed"
        key: str | None = None
        try:
            message = error.errors[0]["message"]  # type: ignore
            key = error.errors[0]["extensions"]["key"]  # type: ignore
        except KeyError:
            pass

        if key == "iteration_not_writable":
            raise LastIterationNotWritableError()
        elif key == "iteration_multiple_active":
            raise MultipleActiveIterationsError()

        raise VecticeException(f"{reference_type}: {message}")


class BadReferenceFactory:
    """Appropriate exceptions for HTTP/GQL errors."""

    @classmethod
    def get_reference(
        cls, reference_type: str, value: str | int, key: str | None = None, message: str | None = None
    ) -> Exception:
        """Get an appropriate error given a reference type.

        Parameters:
            reference_type: The reference type.
            value: A value.

        Returns:
            An exception instance.
        """
        if key == "project_template_not_found" and message:
            return ProjectTemplateError(message)

        if isinstance(value, str) and reference_type == "workspace":
            if not re.search(WORKSPACE_VID_REG, value):
                return WorkspaceNameError(value)
            return WorkspaceIdError(value)
        elif isinstance(value, str) and reference_type == "project":
            if not re.search(PROJECT_VID_REG, value):
                return ProjectNameError(value)
            return ProjectIdError(value)
        elif isinstance(value, str) and reference_type == "phase":
            if not re.search(PHASE_VID_REG, value):
                return PhaseNameError(value)
            return PhaseIdError(value)
        elif reference_type == "step":
            if isinstance(value, str):
                return StepNameError(value)
            elif isinstance(value, int):  # pyright: ignore[reportUnnecessaryIsInstance]
                return StepIdError(value)
        elif isinstance(value, str) and reference_type == "iteration":
            if re.search(ITERATION_VID_REG, value):
                return IterationIdError(value)
            return IterationNameError(value)
        elif isinstance(value, str) and reference_type == "section":
            return SectionNameError(value)
        elif reference_type == "iteration_index":
            if isinstance(value, int):
                return IterationIndexError(value)
        elif isinstance(value, str) and reference_type == "steps":
            return NoStepsInPhaseError(value)
        elif isinstance(value, str) and reference_type == "dataset":
            return DatasetIdError(value)
        elif isinstance(value, str) and reference_type == "dataset_version":
            return DatasetVersionIdError(value)
        elif isinstance(value, str) and reference_type == "model":
            return ModelIdError(value)
        elif isinstance(value, str) and reference_type == "model_version":
            return ModelVersionIdError(value)
        return RuntimeError(f"The value {value} of type {reference_type} is not valid!")


class VecticeException(Exception):  # noqa: N818
    def __init__(self, value: Any):
        super().__init__(value)
        self.__suppress_context__ = True
        self.value = value


class VecticeBaseNameError(NameError):
    def __init__(self, value: Any):
        super().__init__(value)
        self.__suppress_context__ = True
        self.value = value

    def __str__(self):
        divider = "=" * len(f"{self.__class__.__name__}: {self.value}")
        return f"\n{divider}\n{self.__class__.__name__}: {self.value}"


class IDError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(value)


class WorkspaceNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The workspace with name '{value}' is unknown.")


class WorkspaceIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The workspace with id '{value}' is unknown.")


class ProjectNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The project with name '{value}' is unknown.")


class ProjectTemplateError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(value)


class ProjectIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The project with id '{value}' is unknown.")


class PhaseNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The phase with name '{value}' is unknown.")


class PhaseIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The phase with id '{value}' is unknown.")


class StepNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(
            f"The step with name '{value}' is unknown. Use <your iteration>.list_steps() method to find step names."
        )


class StepIdError(VecticeBaseNameError):
    def __init__(self, value: int):
        super().__init__(
            f"The step with id '{value}' is unknown. Use <your iteration>.list_steps() method to find step ids."
        )


class IterationIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The iteration with id '{value}' is unknown.")


class IterationIndexError(VecticeBaseNameError):
    def __init__(self, value: int):
        super().__init__(f"The iteration with index '{value}' is unknown.")


class IterationNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The iteration with name '{value}' is unknown.")


class SectionNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The section {value!r} is unknown.")


class LastIterationNotWritableError(VecticeBaseNameError):
    def __init__(self):
        super().__init__(
            "Your last updated iteration is completed or canceled, but you have at least one previous iteration in progress. Please specify the iteration you wish to access using the 'iteration()' method, or create a new one using 'create_iteration()' method."
        )


class MultipleActiveIterationsError(VecticeBaseNameError):
    def __init__(self):
        super().__init__(
            "You have multiple iterations in progress. Please specify the iteration you wish to access using the 'iteration()' method, or create a new one using 'create_iteration()' method."
        )


class NoStepsInPhaseError(VecticeBaseNameError):
    def __init__(self, value: str):
        ref = f"with id '{value}'" if re.search(PHASE_VID_REG, value) else f"'{value}'"
        super().__init__(f"There are no steps in the phase {ref}. Must create steps for this phase in the Web App.")


class DatasetIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The dataset with id '{value}' is unknown.")


class DatasetVersionIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The dataset version with id '{value}' is unknown.")


class ModelIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The model with id '{value}' is unknown.")


class ModelVersionIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The model version with id '{value}' is unknown.")


class ArtifactVersionIdExistingError(VecticeBaseNameError):
    def __init__(self):
        super().__init__("The asset version is already assigned to the iteration.")
