from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EntityFileOutput:
    fileId: int
    fileName: str
    contentType: str
    entityId: int
    entityType: str
    modelFramework: str | None = None
    publicId: str | None = None
