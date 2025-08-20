from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectice.api.json.json_type import TJSON

if TYPE_CHECKING:
    from vectice.api.json.dataset_version import DatasetVersionOutput
    from vectice.models.property import Property


class DatasetRegisterOutput(TJSON):
    @property
    def dataset_version(self) -> DatasetVersionOutput:
        from vectice.api.json.dataset_version import DatasetVersionOutput

        return DatasetVersionOutput(**self["datasetVersion"])

    @property
    def use_existing_version(self) -> bool:
        return bool(self["useExistingVersion"])

    @property
    def use_existing_dataset(self) -> bool:
        return bool(self["useExistingDataset"])

    # TODO: complete the jobrun property
    @property
    def job_run(self) -> str:
        return str(self["jobRun"])


class DatasetRegisterInput(TJSON):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def data_sources(self) -> list[dict[str, Any]]:
        return list(self["datasetSources"])

    @property
    def dataset_inputs(self) -> list[str] | None:
        return list(self["datasetInputs"]) if self["datasetInputs"] else None

    @property
    def model_inputs(self) -> list[str] | None:
        return list(self["modelInputs"]) if self["modelInputs"] else None

    @property
    def properties(self) -> Property:
        from vectice.models.property import Property

        return Property(**self["properties"])
