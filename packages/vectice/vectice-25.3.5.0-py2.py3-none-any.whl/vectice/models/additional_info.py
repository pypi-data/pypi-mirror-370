from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass
class AdditionalInfo:
    """Defines additional information for a model about his context that a user would like to display in vectice.

    Parameters:
        url: The URL to identify the property.
        run_id: The run ID of the property.
        framework: The framework used for the property.
        extra_info: Additional information related to the model run.
    """

    url: str | None = None
    run: str | None = None
    framework: Framework | None = None
    extra_info: ExtraInfo | list[ExtraInfo] | None = None

    def __post_init__(self):
        if self.run is not None and not isinstance(self.run, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.run = str(self.run)
        if self.url is not None and not isinstance(self.url, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.url = str(self.url)
        if self.framework is not None and not isinstance(
            self.framework, Framework
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.framework = None

    def __repr__(self) -> str:
        return f"AdditionalInfo(url='{self.url}', run_id='{self.run}', framework='{self.framework}', extra_info={self.extra_info})"

    def _format_extra_info(self) -> list[dict[str, str]] | None:
        if self.extra_info is None:
            return None
        elif isinstance(self.extra_info, ExtraInfo):
            return [self.extra_info.asdict()]
        elif isinstance(self.extra_info, list):  # pyright: ignore[reportUnnecessaryIsInstance]
            return [info.asdict() for info in self.extra_info]
        else:
            raise ValueError("Invalid type for extra_info. Should be ExtraInfo, List[ExtraInfo], or None.")

    def asdict(self) -> dict[str, str | Framework | list[dict[str, str]] | None]:
        extra_info_dict = self._format_extra_info()
        return {
            "url": self.url,
            "run": self.run,
            "library": self.framework.value if self.framework is not None else None,
            "extraInfo": extra_info_dict,
        }


class Framework(Enum):
    """Enumeration of the different Experiment Tracker framework."""

    MLFLOW = "MLFLOW"
    WANDB = "WANDB"
    OTHER = "OTHER"


@dataclass
class ExtraInfo:
    """Represent a key value pair of extra information."""

    key: str
    value: str

    def __post_init__(self):
        if not isinstance(self.key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.key = str(self.key)
        if not isinstance(self.value, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.value = str(self.value)

    def asdict(self) -> dict[str, str]:
        return {"key": self.key, "value": self.value}
