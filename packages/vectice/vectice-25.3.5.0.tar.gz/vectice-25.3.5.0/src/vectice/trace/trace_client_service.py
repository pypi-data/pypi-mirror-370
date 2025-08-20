from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Set

from vectice import Connection
from vectice.api.http_error_handlers import VecticeException
from vectice.connection import DEFAULT_HOST
from vectice.services.phase_service import PhaseService

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from vectice.api.client import Client
    from vectice.models.iteration import Iteration, IterationService
    from vectice.models.phase import Phase


class TraceClientService:
    """TraceClientService is a base class for services that interact with the Vectice Trace API.

    It provides functionality to initialize the service and manage the client connection.
    It also manages client configuration, including setting the API token, host, and phase.
    The intermediary logging calls for the Vectice Trace API are handled through this service aswell.
    """

    def __init__(
        self,
        phase: str | None = None,
        create_new_iteration: bool = False,
    ):
        """Initialize the ClientService with a Vectice client.

        :param client: An instance of the Vectice client.
        """
        api_token = self.get_env_api_token()
        host = self.get_env_host()

        self._connection = Connection(api_token=api_token, host=host) if api_token and host else None
        self._client = self._connection._client if self._connection else None  # pyright: ignore[reportPrivateUsage]
        self._phase = self._connection.phase(phase) if self._connection and phase else None

        self._iteration = self.get_active_iteration_or_create(create_new_iteration)
        self._iteration_service = (
            self._iteration._service if self._iteration else None  # pyright: ignore[reportPrivateUsage]
        )

    #### Properties ####

    @property
    def connection(self) -> Connection:
        """Get the Vectice connection."""
        if self._connection is None:
            raise VecticeException("Connection is not initialized. Please set the connection parameters first.")
        return self._connection

    @property
    def client(self) -> Client:
        """Get the Vectice client."""
        if self._client is None:
            raise VecticeException("Client is not initialized. Please set the connection parameters first.")
        return self._client

    @property
    def iteration(self) -> Iteration:
        """Get the current Vectice iteration."""
        if self._iteration is None:
            raise VecticeException("Iteration is not set. Please set the iteration first.")
        return self._iteration

    @property
    def iteration_service(self) -> IterationService:
        """Get the current Vectice iteration."""
        if self._iteration_service is None:
            raise VecticeException("Iteration is not set. Please set the iteration first.")
        return self._iteration_service

    @property
    def phase(self) -> Phase:
        """Get the current Vectice iteration."""
        if self._phase is None:
            raise VecticeException("Phase is not set. Please set the phase first.")
        return self._phase

    #### Utility Methods ####

    @staticmethod
    def get_env_api_token() -> str:
        api_token = os.environ.get("VECTICE_API_TOKEN")
        if not api_token:
            raise VecticeException(
                "`VECTICE_API_TOKEN` is not set. Please set the environmental variable for `VECTICE_API_TOKEN`"
            )
        return api_token

    @staticmethod
    def get_env_host() -> str:
        host = os.environ.get("VECTICE_HOST")
        if not host:
            _logger.warning("`VECTICE_HOST` is not set. Using default host: %s", DEFAULT_HOST)
            return DEFAULT_HOST
        return host

    def is_vectice_client_valid(self):
        """Check if the Vectice client configuration is valid."""
        if self._connection is None:
            raise VecticeException("Vectice connection is not initialized. Please set the connection parameters first.")
        if self._client is None:
            raise VecticeException("Vectice client is not initialized. Please set the connection parameters first.")
        if self._phase is None:
            raise VecticeException("Vectice phase is not set. Please set the phase first.")
        if self._iteration is None:
            raise VecticeException("Vectice iteration is not set. Please set the iteration first.")
        if self._iteration_service is None:
            raise VecticeException("Vectice iteration service is not initialized. Please set the iteration first.")
        return True

    #### Configuration ####

    def get_active_iteration_or_create(self, create_new_iteration: bool) -> Iteration | None:
        """Get the current iteration."""
        if self._phase is None:
            return None
        if create_new_iteration is True:
            iteration = self._phase.create_iteration()
        else:
            iteration = PhaseService(
                self._phase._client  # pyright: ignore[reportPrivateUsage]
            ).get_active_iteration_or_create(self._phase)
        return iteration

    def config(self, phase: str | None = None, create_new_iteration: bool | None = None) -> None:
        """Configure the Vectice trace service with API token, phase, host, and optional prefix."""
        if not self.connection:
            raise VecticeException(
                "Vectice connection is not initialized. Please set `VECTICE_API_TOKEN` and `VECTICE_HOST` environmental variables."
            )

        if phase:
            self._phase = self.connection.phase(phase)

        if create_new_iteration:
            self._iteration = self.get_active_iteration_or_create(create_new_iteration)
            self._iteration_service = self._iteration_service if self._iteration else None

    #### Logging Calls ####

    def save_autolog_assets(self, cells: Set[str], prefix: str | None = None, is_trace: bool = False) -> None:
        """Save autolog assets to the current iteration.

        :param cells: A list of dictionaries containing cell information.
        :param prefix: An optional prefix for the asset names.
        """
        if not cells:
            _logger.warning("No cells to save. Skipping trace assets saving.")
            return

        if prefix is None:
            prefix = self.phase.name
        formatted_cells = [{"cellId": str(cell_id), "content": cell} for cell_id, cell in enumerate(cells) if cell]
        self._iteration_service.save_autolog_assets(formatted_cells, prefix, is_trace)  # type: ignore
