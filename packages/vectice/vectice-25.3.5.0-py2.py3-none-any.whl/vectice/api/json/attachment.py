from __future__ import annotations

from enum import Enum
from typing import Any

from vectice.api.json.json_type import TJSON


class AttachmentTypeEnum(Enum):
    """Enumeration of the attachment type."""

    ENTITY_FILE = "ENTITY_FILE"
    ENTITY_METADATA = "ENTITY_METADATA"


class AttachmentOutput(TJSON):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int:
        return self["id"]

    @property
    def name(self) -> str:
        return self["name"]

    @property
    def type(self) -> AttachmentTypeEnum:
        return AttachmentTypeEnum(self["attachmentType"])

    @property
    def public_id(self) -> str | None:
        if self.get("publicId"):
            return self["publicId"]
        return None
