from __future__ import annotations
from enum import Enum


class Locales(Enum):
    JA = "ja"
    EN = "en"
    ZH = "zh"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str | None) -> Locales:
        if value is None:
            return Locales.OTHER
        try:
            return cls(value.lower())
        except ValueError:
            return Locales.OTHER


class Regions(Enum):
    JP = "jp"
    CN = "cn"

    @classmethod
    def from_str(cls, value: str | None) -> Regions:
        if value is None:
            return Regions.JP
        try:
            return cls(value.lower())
        except ValueError:
            return Regions.JP
