from __future__ import annotations

import importlib
import logging
import os
from functools import reduce
from typing import TYPE_CHECKING, Any, Dict

from vectice.models import AdditionalInfo, Framework
from vectice.models.dataset import TDerivedFrom
from vectice.models.model_exp_tracker import ModelExpTracker
from vectice.utils.common_utils import check_image_path

if TYPE_CHECKING:
    from mlflow import MlflowClient  # pyright: ignore[reportPrivateImportUsage]


_logger = logging.getLogger(__name__)


class MlflowModel(ModelExpTracker):
    def __init__(
        self,
        run_id: str,
        client: MlflowClient,
        url: str | None = None,
        derived_from: list[TDerivedFrom] | None = None,
    ):
        try:
            mlflow = importlib.import_module("mlflow")
            self.mlflow = mlflow
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Mlflow module is required for this method.") from None
        super().__init__(run_id=run_id, client=client, derived_from=derived_from)
        self.url = url
        self._run = self.client.get_run(self.run)
        self.framework = "Mlflow"

    def get_metrics(self) -> Dict[str, Any]:
        metrics = {str(key): value for key, value in self._run.data.metrics.items()}
        return metrics

    def get_properties(self) -> Dict[str, Any]:
        properties = {str(key): value for key, value in self._run.data.params.items()}
        return properties

    def get_attachments(self) -> list[str] | None:
        from mlflow import MlflowException  # pyright: ignore[reportPrivateImportUsage]

        try:
            directory_path = self.mlflow.artifacts.download_artifacts(artifact_uri=self._run.info.artifact_uri + "/")
            return self._get_all_images_in_path(directory_path)
        except MlflowException:
            return None

    def get_name(self) -> str | None:
        if self._run.info.run_name:
            return str(self._run.info.run_name)
        elif self._run.data.tags.get("mlflow.runName"):
            return str(self._run.data.tags["mlflow.runName"])
        return None

    def get_additional_info(self) -> AdditionalInfo:
        additional_info = AdditionalInfo(url=self.url, run=self.run, framework=Framework.MLFLOW)
        return additional_info

    def _get_all_images_in_path(self, path: str) -> list[str]:
        def get_images_in_path(acc: list[str], curr: str) -> list[str]:
            file_full_path = f"{path}/{curr}" if path[-1] != "/" else f"{path}{curr}"
            if not os.path.isfile(os.path.join(path, curr)):
                return [*acc, *self._get_all_images_in_path(file_full_path)]
            else:
                try:
                    is_image = check_image_path(file_full_path)
                    if is_image is True:
                        return [*acc, file_full_path]
                except ValueError:
                    pass

            return acc

        try:
            paths = os.listdir(path)
        except FileNotFoundError:
            return []

        if len(paths) > 100:
            _logger.warning("WARNING: Vectice only captures the first 100 mlflow artifacts.")
        return sorted(reduce(get_images_in_path, paths[:100], []))
