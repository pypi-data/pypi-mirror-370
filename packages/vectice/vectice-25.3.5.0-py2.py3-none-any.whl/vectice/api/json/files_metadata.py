from __future__ import annotations

from dataclasses import dataclass, field
from enum import EnumMeta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class FileMetadataType(EnumMeta):
    """Enumeration of the supported types of resources."""

    Folder = "Folder"
    CsvFile = "CsvFile"
    ImageFile = "ImageFile"
    ExcelFile = "ExcelFile"
    TextFile = "TextFile"
    MdFile = "MdFile"
    DataSet = "DataSet"
    DataTable = "DataTable"
    File = "File"
    Notebook = "Notebook"


@dataclass
class FileMetadata:
    name: str | None = None
    id: str | None = None
    parentId: str | None = None
    path: str | None = None
    type: FileMetadataType | str | None = None
    isFolder: bool | None = False
    children: list[FileMetadata] = field(default_factory=list)
    size: int | None = 0
    uri: str | None = None
    generation: str | None = None
    digest: str | None = None
    itemCreatedDate: datetime | None = None
    itemUpdatedDate: datetime | None = None

    def append(self, child: FileMetadata):
        return self.children.append(child)
