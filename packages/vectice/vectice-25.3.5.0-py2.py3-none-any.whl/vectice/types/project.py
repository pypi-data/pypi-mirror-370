from __future__ import annotations

from typing import TypedDict


class ProjectInput(TypedDict):
    name: str
    description: str | None
    template: str | None
    copy_project_id: str | None
