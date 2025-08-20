from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.api.json.json_type import TJSON
from vectice.api.json.metric import MetricInput

if TYPE_CHECKING:
    from vectice.api.json.model_version import ModelVersionOutput, ModelVersionStatus
    from vectice.models.property import Property


class ModelRegisterOutput(TJSON):
    @property
    def model_version(self) -> ModelVersionOutput:
        from vectice.api.json.model_version import ModelVersionOutput

        return ModelVersionOutput(**self["modelVersion"])

    @property
    def use_existing_model(self) -> bool:
        return bool(self["useExistingModel"])

    # TODO: complete the jobrun property
    @property
    def job_run(self) -> str:
        return str(self["jobRun"])


class ModelRegisterInput(TJSON):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def model_type(self) -> str:
        return str(self["modelType"])

    @property
    def properties(self) -> Property:
        from vectice.models.property import Property

        return Property(**self["properties"])

    @property
    def metrics(self) -> list[MetricInput]:
        return [MetricInput(**metric) for metric in self["metrics"]]

    @property
    def status(self) -> ModelVersionStatus:
        from vectice.api.json.model_version import ModelVersionStatus

        return ModelVersionStatus(self["status"])

    @property
    def framework(self) -> str | None:
        return str(self["framework"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def algorithm_name(self) -> str | None:
        return str(self["algorithmName"])

    @property
    def uri(self) -> str:
        return str(self["uri"])

    @property
    def dataset_inputs(self) -> list[str] | None:
        return list(self["datasetInputs"]) if self["datasetInputs"] else None

    @property
    def model_inputs(self) -> list[str] | None:
        return list(self["modelInputs"]) if self["modelInputs"] else None

    @property
    def context(self) -> ModelVersionContextInput:
        return ModelVersionContextInput(self["context"])


class ModelVersionContextInput(TJSON):
    @property
    def url(self) -> str:
        return str(self["url"])

    @property
    def run(self) -> str:
        return str(self["run"])
