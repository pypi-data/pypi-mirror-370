from __future__ import annotations

import json
from typing import TYPE_CHECKING

from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

if TYPE_CHECKING:
    from vectice.autolog.model_types import ModelTypes


def _get_non_default_params(step: BaseEstimator):
    """Return parameters that differ from the default values."""
    default_params = type(step)().get_params(deep=False)
    current_params = step.get_params(deep=False)
    non_default_params = {}
    for key, value in current_params.items():
        if key not in default_params or default_params[key] != value:
            non_default_params[key] = value
    return non_default_params


def get_params_recursive(step: BaseEstimator):
    """Return parameters in a serializable format."""
    if hasattr(step, "get_params"):
        params = _get_non_default_params(step)
        serializable_params = {}
        for key, value in params.items():
            if hasattr(value, "get_params"):
                serializable_params[key] = get_params_recursive(value)
            else:
                try:
                    value = json.dumps(value)  # Test if the value is serializable
                    serializable_params[key] = value
                except TypeError:
                    serializable_params[key] = str(value)
        return serializable_params
    else:
        return str(step)


def process_step(step: BaseEstimator):
    """Process each step in the pipeline, handling nested pipelines and column transformers."""
    if isinstance(step, Pipeline):
        steps = []
        for name, sub_step in step.steps:
            steps.append({"name": name, "type": type(sub_step).__name__, "parameters": process_step(sub_step)})
        return {"type": "Pipeline", "steps": steps}
    elif isinstance(step, ColumnTransformer):
        transformers = []
        for name, transformer, columns in step.transformers:
            transformers.append(
                {
                    "name": name,
                    "type": type(transformer).__name__,
                    "columns": columns,
                    "parameters": process_step(transformer) if hasattr(transformer, "get_params") else str(transformer),
                }
            )
        return {"type": "ColumnTransformer", "transformers": transformers}
    else:
        return {"type": type(step).__name__, "parameters": get_params_recursive(step)}


def pipeline_to_json(pipeline: ModelTypes) -> str | None:
    """Convert the entire pipeline to a JSON-compatible dictionary."""
    try:
        if isinstance(pipeline, Pipeline):
            pipeline_dict = process_step(pipeline)
            return json.dumps(pipeline_dict, indent=4)
    except Exception:
        pass
    return None
