from io import IOBase
from typing import Any, Union

from PIL.Image import Image

from vectice.utils.common_utils import check_file_path, check_image_path


def is_image_or_file(value: Any) -> Union[Image, str, IOBase, None]:
    return is_pil_image(value) or is_binary(value) or is_existing_image_path(value) or is_existing_file_path(value)


def is_pil_image(value: Any) -> Union[Image, None]:
    return value if isinstance(value, Image) else None


def is_binary(value: Any) -> Union[IOBase, None]:
    return value if isinstance(value, IOBase) else None


def is_existing_image_path(value: Any):
    return value if isinstance(value, str) and check_image_path(value) else None


def is_existing_file_path(value: Any):
    return value if isinstance(value, str) and check_file_path(value) else None
