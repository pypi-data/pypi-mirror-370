from typing import Any

from vectice.api.json.json_type import TJSON


class DatasetOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])


class DatasetVersionOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if "dataSet" in self:
            self._dataset: DatasetOutput = DatasetOutput(**self["dataSet"])
        else:
            self._dataset = None  # type: ignore

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def dataset(self) -> DatasetOutput:
        return self._dataset

    @property
    def lineage(self) -> dict:
        return self["origin"]

    @property
    def origin_id(self) -> int:
        return int(self["origin"]["id"])
