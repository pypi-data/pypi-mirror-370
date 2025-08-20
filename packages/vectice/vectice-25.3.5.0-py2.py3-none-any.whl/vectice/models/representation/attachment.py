from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class Attachment:
    id: int
    name: str
    type: Literal["table", "file"]
