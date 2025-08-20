from __future__ import annotations

from typing import Any

from vectice.autolog.model_library import ModelLibrary


class TechniqueService:

    def _get_model_technique(self, model_object: Any, libary: ModelLibrary):
        if libary is ModelLibrary.STATSMODEL:
            algorithm = str(model_object.model.__class__).split(".")[-1]  # type: ignore[reportAttributeAccessIssue]
        elif libary is ModelLibrary.SKLEARN_PIPELINE:
            try:
                algorithm = str(model_object.steps[-1][-1].__class__).split(".")[-1]  # type: ignore[reportAttributeAccessIssue]
            except Exception:
                algorithm = str(model_object.__class__).split(".")[-1]
        else:
            algorithm = str(model_object.__class__).split(".")[-1]

        return algorithm.replace("'>", "")
