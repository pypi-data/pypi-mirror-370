from __future__ import annotations

from functools import reduce
from typing import Type, TypeVar, overload

from vectice.api.json.json_type import TJSON

ItemType = TypeVar("ItemType")


@overload
def json_to_class(json: TJSON, cls: Type[ItemType]) -> ItemType: ...


@overload
def json_to_class(json: list[TJSON], cls: Type[ItemType]) -> list[ItemType]: ...


def json_to_class(json: TJSON | list[TJSON], cls: Type[ItemType]) -> ItemType | list[ItemType]:
    if isinstance(json, list):
        return reduce(lambda acc, curr: [*acc, cls(**curr)], json, [])

    return cls(**json)
