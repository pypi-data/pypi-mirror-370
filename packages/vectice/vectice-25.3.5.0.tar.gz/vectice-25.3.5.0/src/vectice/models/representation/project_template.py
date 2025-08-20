from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProjectTemplate:
    name: str
    description: str | None = None
