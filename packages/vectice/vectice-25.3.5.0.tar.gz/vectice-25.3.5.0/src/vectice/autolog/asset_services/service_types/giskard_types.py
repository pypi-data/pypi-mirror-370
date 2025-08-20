from __future__ import annotations

from enum import Enum


class GiskardType(Enum):
    RAG = "RAG"
    SCAN = "SCAN"
    QATESTSET = "QATESTSET"
    TEST_SUITE_RESULT = "TEST_SUITE_RESULT"
