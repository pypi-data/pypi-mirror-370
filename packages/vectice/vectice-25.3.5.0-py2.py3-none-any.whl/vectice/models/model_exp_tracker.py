from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from vectice.models import AdditionalInfo, Metric, Property
from vectice.models.dataset import TDerivedFrom
from vectice.models.model import Model


class ModelExpTracker(ABC):
    """Base class for Experiment Tracker Wrapper like Mlflow.

    The ModelExpTracker subclasses are used to wrap an experiment tracker model into a Vectice model.
    The `as_vectice_model` method combines the retrieved metrics, properties, attachments, name,
    and derived_from information to create a Vectice Model object representing the
    experiment tracker model.

    Args:
        run: The ID of the experiment run.
        client: The client object used for interacting with the experiment tracking system.
        _derived_from (Optional): A list of derived models from which the
            current model is derived.

    Methods to be implemented:
        get_metrics: Abstract method to retrieve metrics associated with the model.
        get_properties: Abstract method to retrieve properties associated with the model.
        get_attachments: Abstract method to retrieve attachments associated with the model.
        get_name: Abstract method to retrieve the name of the model.

    """

    def __init__(
        self,
        run_id: str,
        client: Any,
        derived_from: list[TDerivedFrom] | None = None,
    ):
        self.run: str = run_id
        self.client = client
        self._derived_from: list[TDerivedFrom] | None = derived_from
        self.name = None

    @abstractmethod
    def get_metrics(self) -> dict[str, int | float] | list[Metric] | Metric | None:
        pass

    @abstractmethod
    def get_properties(self) -> dict[str, str | int] | list[Property] | Property | None:
        pass

    @abstractmethod
    def get_attachments(self) -> list[str] | None:
        pass

    @abstractmethod
    def get_name(self) -> str | None:
        pass

    @abstractmethod
    def get_additional_info(self) -> dict[str, str] | AdditionalInfo | None:
        pass

    def as_vectice_model(self) -> Model:
        metrics = self.get_metrics()
        properties = self.get_properties()
        attachments = self.get_attachments()
        name = self.get_name()
        additional_info = self.get_additional_info()
        model = Model(
            name=name,
            library=None,
            technique=None,
            metrics=metrics,
            properties=properties,
            attachments=attachments,
            derived_from=self._derived_from,
            additional_info=additional_info,
        )
        return model
