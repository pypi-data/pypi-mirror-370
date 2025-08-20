from __future__ import annotations

from typing import List, Union

from vectice.models.table import Table

TFormattedAttachment = Union[Table, str]
TAttachment = Union[str, List[str], Table, List[Table], List[TFormattedAttachment]]
