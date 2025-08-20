from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Page:
    """Simple structure to allow paging when requesting list of elements."""

    index: int = 1
    """The index of the page."""
    size: int = 100
    """The size of the page."""
    afterCursor: bool | None = False

    hasNextPage: bool | None = False
