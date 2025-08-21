from __future__ import annotations
from enum import Enum


class EventTypes(Enum):
    REGULAR = "REGULAR"
    REPEATING = "REPEATING"
    ALL_DAY = "ALL_DAY"
    TEMPORARY = "TEMPORARY"
    OTHER = "OTHER"

    @classmethod
    def from_str(cls, s: str) -> EventTypes:
        try:
            return cls(s)
        except ValueError:
            return cls.OTHER


class OperationTypes(Enum):
    ADD = "add"
    MODIFY = "modify"
    REMOVE = "remove"
    OTHER = "other"

    @classmethod
    def from_str(cls, s: str) -> OperationTypes:
        try:
            return cls(s)
        except ValueError:
            return cls.OTHER
