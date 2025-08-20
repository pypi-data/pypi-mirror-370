from __future__ import annotations

import logging
import math
import mimetypes
import os
import pickle  # nosec
import re
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from enum import Enum
from functools import reduce
from io import BufferedReader, BytesIO, IOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Sequence, Union

from PIL import Image, ImageFile
from rich.console import Console
from rich.table import Table

from vectice.api.http_error_handlers import VecticeException
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.iteration import IterationStatus
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput
from vectice.models.attachment import TAttachment, TFormattedAttachment
from vectice.models.metric import Metric
from vectice.models.property import Property
from vectice.models.table import Table as VecticeTable
from vectice.utils.filesize import size

if TYPE_CHECKING:
    from vectice.api.client import Client
    from vectice.api.json.dataset_version import DatasetVersionOutput
    from vectice.api.json.model_version import ModelVersionOutput
    from vectice.models.dataset import Dataset
    from vectice.models.iteration import Iteration
    from vectice.models.model import Model

TVersionOutput = Union[DatasetVersionRepresentationOutput, ModelVersionRepresentationOutput]


@contextmanager
def hide_logs(package: str):
    old_level = logging.getLogger(package).level
    try:
        logging.getLogger(package).setLevel(logging.ERROR)
        yield
    finally:
        logging.getLogger(package).setLevel(old_level)


def check_read_only(iteration: Iteration):
    """Check if an iteration is completed or cancelled.

    Refreshing the iteration is necessary because in a Jupyter notebook
    its status could have changed on the backend.

    Parameters:
        iteration: The iteration to check.

    Raises:
        RuntimeError: When the iteration is read-only (completed or cancelled).
    """
    refresh_iteration = iteration._phase.iteration(iteration.index)  # pyright: ignore[reportPrivateUsage]
    if refresh_iteration._status in {  # pyright: ignore[reportPrivateUsage]
        IterationStatus.Completed,
        IterationStatus.Abandoned,
    }:
        raise RuntimeError(f"The Iteration is {refresh_iteration.status} and is read-only.")


def check_image_path(path: str) -> bool:
    if _check_for_comment(path):
        return False
    try:
        check_path = Path(path).exists()
    except OSError:
        return False
    _, ext = os.path.splitext(path)
    pillow_extensions = {exten for exten in Image.registered_extensions()}
    if not check_path and ext in pillow_extensions:
        raise ValueError("Check the file path.")
    if ext not in pillow_extensions:
        return False
    return True


def check_file_path(path: str) -> bool:
    if _check_for_comment(path):
        return False
    try:
        check_image_path(path)
    except ValueError:
        raise ValueError("Check the file path.") from None
    _, ext = os.path.splitext(path)
    mime_type = mimetypes.guess_type(path)[0]
    if not mime_type and ext not in [".parquet", ".ipynb"]:
        return False
    return True


def _check_for_comment(path: str) -> bool:
    _, ext = os.path.splitext(path)
    if ext:
        return False
    return True


def _validate_image_or_file(path: str) -> BufferedReader:
    try:
        return open(path, "rb")
    except FileNotFoundError:
        raise ValueError(f"The provided file {path!r} cannot be opened. Check its format and permissions.") from None


def get_image_or_file_variables(value: str | IOBase | Image.Image) -> tuple[BufferedReader | IOBase | BytesIO, str]:
    if isinstance(value, IOBase):
        image = value
        filename = os.path.basename(value.name)  # type: ignore[attr-defined]
        return image, filename
    if isinstance(value, str):
        image = _validate_image_or_file(value)
        filename = os.path.basename(image.name)
        return image, filename
    if isinstance(value, Image.Image):  # pyright: ignore[reportUnnecessaryIsInstance]
        previous_load_truncated_images = ImageFile.LOAD_TRUNCATED_IMAGES
        previous_max_image_pixels = Image.MAX_IMAGE_PIXELS
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.MAX_IMAGE_PIXELS = None
        in_mem_file = BytesIO()
        value.save(in_mem_file, format=value.format)
        in_mem_file.seek(0)
        filename = os.path.basename(value.filename)  # type: ignore #TODO I doubt filename really exists in PIL: https://stackoverflow.com/questions/45087638/get-image-filename-from-image-pil
        ImageFile.LOAD_TRUNCATED_IMAGES = previous_load_truncated_images
        Image.MAX_IMAGE_PIXELS = previous_max_image_pixels
        return in_mem_file, filename

    raise ValueError("Unsupported image provided.")


def temp_print(string: str | None = None, table: Table | None = None) -> None:
    console = Console(width=120)
    if string:
        print(string)
        print()
    if table:
        console.print(table)
        print()


def convert_keys_to_camel_case(input_dict: Dict[str, Any]) -> Dict[str, Union[Any, Dict[str, Any]]]:
    camel_case_dict: Dict[str, Union[Any, Dict[str, Any]]] = {}

    for key, value in input_dict.items():
        camel_case_key = re.sub(r"_([a-z])", lambda match: match.group(1).upper(), key)
        if isinstance(value, dict):
            value = convert_keys_to_camel_case(value)
        camel_case_dict[camel_case_key] = value

    return camel_case_dict


def capture_unique_attachments(attachments: tuple[list[str], list[VecticeTable]], curr: TFormattedAttachment | Any):
    str_list, table_list = attachments
    if isinstance(curr, str):
        if curr not in str_list:
            return [*str_list, curr], table_list
    elif isinstance(curr, VecticeTable):
        if curr not in table_list:
            return str_list, [*table_list, curr]
    else:
        raise ValueError(
            f"The element '{curr}' in 'attachments' is of type '{type(curr)}', which is invalid. Only strings and Vectice Tables instances are supported."
        )
    return str_list, table_list


def format_attachments(attachments: TAttachment) -> list[TFormattedAttachment]:
    if not isinstance(attachments, list):
        attachments = [attachments]
    str_list, table_list = reduce(capture_unique_attachments, attachments, ([], []))
    list_attachments = [*str_list, *table_list]

    for attachment in list_attachments:
        if not isinstance(attachment, str) and not isinstance(
            attachment, VecticeTable
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(
                f"Argument 'attachments' with type '{type(attachment)}' is invalid, only str and tables are supported."
            )
    return list_attachments


def check_string_sanity(value: str):
    if value == "":
        raise VecticeException("Cannot assign an empty comment. Please provide a valid comment")


def ensure_correct_project_id_from_representation_objs(project_id: str, value: Any):
    from vectice.models.representation.dataset_representation import DatasetRepresentation
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_representation import ModelRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    if (
        isinstance(value, DatasetRepresentation)
        or isinstance(value, DatasetVersionRepresentation)
        or isinstance(value, ModelRepresentation)
        or isinstance(value, ModelVersionRepresentation)
    ) and value.project_id != project_id:
        raise VecticeException("Assigning an asset coming from another project is forbidden")


def set_model_attachments(
    client: Client, model: Model, model_version: ModelVersionOutput
) -> tuple[list[str] | None, bool]:
    from vectice.models.attachment_container import AttachmentContainer

    logging.getLogger("vectice.models.attachment_container").propagate = True
    attachments = None
    if model.attachments:
        container = AttachmentContainer(model_version, client)
        attachments = container.upsert_attachments(model.attachments)

    success_pickle: bool = False
    if model.predictor is not None:
        try:
            model_content = _serialize_model(model.predictor)
            model_type_name = type(model.predictor).__name__
            container = AttachmentContainer(model_version, client)
            container.add_serialized_model(model_type_name, model_content)
            success_pickle = True
        except Exception:
            success_pickle = False

    return attachments, success_pickle


def set_dataset_attachments(client: Client, dataset: Dataset, dataset_version: DatasetVersionOutput):
    from vectice.models.attachment_container import AttachmentContainer

    logging.getLogger("vectice.models.attachment_container").propagate = True
    attachments = None
    if dataset.attachments:
        container = AttachmentContainer(dataset_version, client)
        attachments = container.upsert_attachments(dataset.attachments)
    return attachments


def _serialize_model(model: Any) -> bytes:
    return pickle.dumps(model)


def repr_class(class_object: object) -> str:
    attributes = [
        (key, value.value if isinstance(value, Enum) else value)
        for key, value in vars(class_object).items()
        if not key.startswith("_")
    ]
    attribute_strings = [f"{key} = {value}" for key, value in attributes]
    return f'{class_object.__class__.__name__}({", ".join(attribute_strings)})'


def strip_dict_list(dict_list: List[Dict[str, str | int]]) -> List[Dict[str, str | int]]:
    cleaned_list = []
    for item in dict_list:
        if "value" in item:
            if isinstance(item["value"], str):
                cleaned_value = re.sub(r"\s{2,}", " ", item["value"].replace("\n", ""))
                item["value"] = cleaned_value

            cleaned_list.append(item)
    return cleaned_list


def remove_type_name(dict_list: Sequence[Dict[str, Any]]) -> Sequence[Dict[str, Any]]:
    for item in dict_list:
        stack = [item]

        while stack:
            current = stack.pop()

            if "__typename" in current:
                del current["__typename"]

            for _, value in current.items():
                if isinstance(value, dict):
                    stack.append(value)
                elif isinstance(value, list):
                    for sub_item in value:
                        if isinstance(sub_item, dict):
                            stack.append(sub_item)

    return dict_list


def convert_list_keyvalue_to_dict(list_kv: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {item["key"]: item["value"] for item in list_kv}


def process_versions_list_metrics_and_properties(
    dict_list: List[TVersionOutput],
) -> List[Dict[str, Any]]:
    return_dict: List[Dict[str, Any]] = []

    for item in dict_list:
        if "metrics" in item:
            item["metrics"] = convert_list_keyvalue_to_dict(item["metrics"])
        if "properties" in item:
            item["properties"] = strip_dict_list(item["properties"])
            item["properties"] = convert_list_keyvalue_to_dict(item["properties"])
        return_dict.append(item)
    return return_dict


def process_versions_origins(dict_list: Sequence[Dict[str, Any]]) -> Sequence[Dict[str, Any]]:
    for item in dict_list:
        if "origins" in item:
            origins = item["origins"]
            if "phase" in origins:
                if origins["phase"] is not None and "vecticeId" in origins["phase"]:
                    item["phase_origin"] = origins["phase"]["vecticeId"]
                else:
                    item["phase_origin"] = "Unknown"
            if "iteration" in origins:
                if origins["iteration"] is not None and "vecticeId" in origins["iteration"]:
                    item["iteration_origin"] = origins["iteration"]["vecticeId"]
                else:
                    item["iteration_origin"] = "Unknown"
            del item["origins"]

    return dict_list


def flatten_resources(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    def _get_resource_dict(res: Dict[str, Any]):
        resource_size = res.get("size", None)
        return {
            "number_of_items": res.get("number_of_items", None),
            "total_number_of_columns": res.get("total_number_of_columns", None),
            "size": size(int(resource_size)) if resource_size is not None else None,
        }

    flattened_resource = {}
    if len(resources) > 1 or (resources[0]["resource_type"] != "GENERIC"):
        flattened_resource = {}
        for res in resources:
            resource_type = res.pop("resource_type")
            flattened_resource[resource_type] = _get_resource_dict(res)
    else:
        flattened_resource = _get_resource_dict(resources[0])
    return flattened_resource


def flatten_dict(dictionary: Dict[str, Any], parent_key: str = "", separator: str = "_") -> Dict[str, Any]:
    flattened_dict = {}
    for key, value in dictionary.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, separator))
        else:
            flattened_dict[new_key] = value
    return flattened_dict


def convert_to_snake_case(key: str) -> str:
    snake_case_key = "".join(["_" + i.lower() if i.isupper() else i for i in key]).lstrip("_")
    return snake_case_key


def convert_keys_to_snake_case(dictionary: TVersionOutput) -> TVersionOutput:
    converted_dict = (
        ModelVersionRepresentationOutput({})
        if isinstance(dictionary, ModelVersionRepresentationOutput)
        else DatasetVersionRepresentationOutput({})
    )
    for k, v in dictionary.items():
        if k == "vecticeId":
            converted_dict["id"] = v
        else:
            converted_dict[convert_to_snake_case(k)] = v
    return converted_dict


def format_metrics(metrics: dict[str, int | float] | list[Metric] | Metric | None) -> list[Metric]:
    if metrics is None:
        return []
    if isinstance(metrics, Metric):
        return [metrics]
    if isinstance(metrics, list):
        metrics = _remove_incorrect_metrics(metrics)
        key_list = [metric.key for metric in metrics]
        check_key_duplicates(key_list)
        return metrics
    if isinstance(metrics, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        return [Metric(key, value) for (key, value) in metrics.items()]
    else:
        raise ValueError("Please check metric type.")


def format_properties(properties: dict[str, str | int] | list[Property] | Property | None) -> list[Property]:
    if properties is None:
        return []
    if isinstance(properties, Property):
        return [properties]
    if isinstance(properties, list):
        properties = _remove_incorrect_properties(properties)
        key_list = [prop.key for prop in properties]
        check_key_duplicates(key_list)
        return properties
    if isinstance(properties, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        return [Property(key, str(value)) for (key, value) in properties.items()]
    else:
        raise ValueError("Please check property type.")


def check_key_duplicates(key_list: list[str]):
    if len(key_list) != len(set(key_list)):
        raise ValueError("Duplicate keys are not allowed.")


def _remove_incorrect_properties(properties: list[Property]) -> list[Property]:
    for prop in properties:
        if not isinstance(prop, Property):  # pyright: ignore[reportUnnecessaryIsInstance]
            logging.warning(f"Incorrect property '{prop}'. Please check property type.")
            properties.remove(prop)
    return properties


def _remove_incorrect_metrics(metrics: list[Metric]) -> list[Metric]:
    for metric in metrics:
        if not isinstance(metric, Metric):  # pyright: ignore[reportUnnecessaryIsInstance]
            logging.warning(f"Incorrect metric '{metric}'. Please check metric type.")
            metrics.remove(metric)
    return metrics


def get_notebook_path() -> str | None:
    import ipynbname
    from IPython.core.getipython import get_ipython

    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        return None

    ipython = get_ipython()
    if ipython:
        local_vars = ipython.user_global_ns
    else:
        return None
    # VS Code notebook path
    nb_full_path = local_vars.get("__vsc_ipynb_file__")
    if nb_full_path:
        return nb_full_path

    try:
        nb_path = ipynbname.path()
        nb_full_path = os.path.join(os.getcwd(), nb_path.name)
    except Exception:
        nb_full_path = None

    return nb_full_path


def get_script_path() -> str | None:
    # Get the full path of the current script
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        return None
    try:
        return sys.argv[0]
    except Exception:
        pass
    return None


def check_for_git_or_code_file() -> tuple[bool, bool]:
    from vectice.models.code_version import _look_for_git_repository  # pyright: ignore[reportPrivateUsage]

    code_source_file = get_notebook_path() or get_script_path()
    bool_code_source_file = bool(code_source_file)
    bool_repo = bool(_look_for_git_repository())

    return bool_code_source_file, bool_repo


@contextmanager
def suppress_logging(logger_name: str, level: int = logging.CRITICAL):
    logger = logging.getLogger(logger_name)
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(previous_level)


def wait_for_path(path: str, timeout: int = 10, interval: int | float = 1) -> str:
    start_time = time.time()
    while not os.path.exists(path):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Path {path} did not appear within {timeout} seconds")
        time.sleep(interval)
    return path


def temp_directory(name: str) -> Path:
    """Create a temporary directory."""
    temp_dir = Path(tempfile.gettempdir()) / name
    if temp_dir.exists():
        return temp_dir
    temp_dir.mkdir(exist_ok=True)
    return temp_dir


def get_asset_name(variable: str, phase_name: str, prefix: str | None = None) -> str:
    if prefix is None:
        return f"{phase_name}-{variable}"
    elif prefix == "":
        return variable
    return f"{prefix}-{variable}"


def safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        import math

        float_val = float(val)
        return None if math.isnan(float_val) else float_val
    except (TypeError, ValueError):
        return None


def to_datetime_safe(ts: float | None) -> str | None:
    if ts is None or (isinstance(ts, float) and math.isnan(ts)):
        return None
    return datetime.fromtimestamp(ts / 1000, timezone.utc).isoformat()
