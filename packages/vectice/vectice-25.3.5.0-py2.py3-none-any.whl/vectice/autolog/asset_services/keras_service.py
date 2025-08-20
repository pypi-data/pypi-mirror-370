from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.utils.common_utils import get_asset_name, temp_directory

if TYPE_CHECKING:
    from keras import Model as KerasModel  # type: ignore[reportMissingImports]  # type: ignore[reportMissingImports]
    from keras.layers import InputLayer  # type: ignore[reportMissingImports]
    from keras.models import Model as KerasModel  # type: ignore[reportMissingImports]


KERAS_TEMP_DIR = "keras"

_logger = logging.getLogger(__name__)


class AutologKerasService(MetricService, TechniqueService):
    def __init__(
        self,
        key: str,
        asset: KerasModel,
        data: dict,
        custom_metrics_data: set[str | None],
        phase_name: str,
        prefix: str | None = None,
    ):
        self._asset = asset
        self._key = key
        self._temp_dir = temp_directory(KERAS_TEMP_DIR)
        self._model_name = get_asset_name(self._key, phase_name, prefix)

        super().__init__(cell_data=data, custom_metrics=custom_metrics_data)

    def get_asset(self):
        model_metrics = self._get_model_metrics(self._cell_data)
        training_metrics = self._get_keras_training_metrics(self._asset)
        temp_file_path = self._get_keras_graph()
        _, params = self._get_keras_info(self._asset)

        model = Model(
            library=ModelLibrary.KERAS.value,
            technique=self._get_model_technique(self._asset, ModelLibrary.KERAS),
            metrics=model_metrics.update(training_metrics),
            properties=params,
            name=self._model_name,
            predictor=self._asset,
            attachments=temp_file_path,
        )
        return {
            "variable": self._key,
            "model": model,
            "asset_type": VecticeType.MODEL,
        }

    def _format_keras_params(self, model: KerasModel) -> dict[str, Any]:
        params: dict[str, Any] = {}

        def _get_output_shape(layer: InputLayer) -> tuple:
            try:
                # Keras 2.15.1 & below
                return layer.output_shape
            except AttributeError:
                return layer.output.shape  # pyright: ignore[reportAttributeAccessIssue]

        for i, layer in enumerate(model.layers):
            output_shape = _get_output_shape(layer)
            params[f"Layer-{i}"] = {
                "name": layer.name,
                "param": layer.count_params(),
                "output shape": output_shape,
            }
        params["Total # of weights"] = model.count_params()

        return params

    def _get_keras_info(self, model: KerasModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            return "keras", self._format_keras_params(model)
        except Exception:
            return None, None

    def _get_keras_graph(self) -> str | None:
        graph = None
        try:
            from keras.utils import plot_model  # type: ignore[reportMissingImports]

            json_file_name = self._temp_dir / f"{self._key}_plot.png"
            temp_file_path = json_file_name.as_posix()
            graph = plot_model(self._asset, to_file=temp_file_path, show_shapes=True, show_layer_names=False)

            if graph is None:
                temp_file_path = None
                _logger.info(
                    "Unable to generate the model plot. Please check the 'plot_model' function from the Keras library is working correctly. Make sure that the graphviz and pydot packages are installed and configured properly."
                )
            return temp_file_path

        except Exception as e:
            _logger.info(
                f"Unable to generate the model plot. Ensure that the Keras library is correctly installed and up-to-date. Error details: {e}"
            )
        return None
