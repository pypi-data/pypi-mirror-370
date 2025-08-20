from __future__ import annotations

from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ExtraMetadata:
    key: str
    value: str | None
    display_name: str | None
