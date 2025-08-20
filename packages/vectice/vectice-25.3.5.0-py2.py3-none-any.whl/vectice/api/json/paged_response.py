from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from functools import reduce
from typing import Generic, Type, TypeVar

from vectice.api.json.json_type import TJSON
from vectice.api.json.page import Page

ItemType = TypeVar("ItemType")


@dataclass
class PagedResponse(Generic[ItemType]):
    """Generic structure describing a result of a paged request.

    The structure contains page information and the list of items for this page.
    """

    total: int
    """Total number of available pages."""
    list: list[ItemType] = field(init=False)
    """Current list of elements for this page."""
    current_page: Page = field(init=False)
    """Information on the current page."""
    page: InitVar[TJSON]
    item_cls: InitVar[Type[ItemType]]
    items: InitVar[list[TJSON]]

    def __post_init__(self, page: TJSON, cls: Type[ItemType], items: list[TJSON]):
        self.current_page = Page(**page)
        self.list = reduce(lambda acc, curr: [*acc, cls(**curr)], items, [])
