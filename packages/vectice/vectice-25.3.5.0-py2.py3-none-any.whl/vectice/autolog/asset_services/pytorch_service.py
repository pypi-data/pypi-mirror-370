from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.asset_services.service_types.vectice_types import VecticeType
from vectice.autolog.asset_services.technique_service import TechniqueService
from vectice.autolog.model_library import ModelLibrary
from vectice.models.model import Model
from vectice.utils.common_utils import get_asset_name

if TYPE_CHECKING:
    from torch.nn import Module
    from torch.nn import Module as TorchModel


class AutologPytorchService(MetricService, TechniqueService):
    def __init__(
        self,
        key: str,
        asset: Module,
        data: dict,
        custom_metrics_data: set[str | None],
        phase_name: str,
        prefix: str | None = None,
    ):
        self._asset = asset
        self._key = key
        self._model_name = get_asset_name(self._key, phase_name, prefix)

        super().__init__(cell_data=data, custom_metrics=custom_metrics_data)

    def get_asset(self):
        _, params = self._get_pytorch_info(self._asset)

        model = Model(
            library=ModelLibrary.PYTORCH.value,
            technique=self._get_model_technique(self._asset, ModelLibrary.PYTORCH),
            metrics=self._get_model_metrics(self._cell_data),
            properties=params,
            name=self._model_name,
            predictor=self._asset,
        )
        return {
            "variable": self._key,
            "model": model,
            "asset_type": VecticeType.MODEL,
        }

    def _format_pytorch_params(self, model: TorchModel) -> dict[str, Any]:
        params: dict[str, Any] = {}

        model_layers = list(model.children())
        # Get the parameters of each layer
        total_params = sum(param.numel() for param in model.parameters())
        for i, layer in enumerate(model_layers):
            layer_params = sum(param.numel() for param in layer.parameters())
            output_shape = layer.out_features if hasattr(layer, "out_features") else None
            params[f"Layer-{i}"] = {
                "name": layer._get_name(),  # pyright: ignore[reportPrivateUsage]
                "param": layer_params,
                "output shape": output_shape,
            }
            params["Total # of weights"] = total_params

        return params

    def _get_pytorch_info(self, model: TorchModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            return "torch", self._format_pytorch_params(model)
        except Exception:
            return None, None
