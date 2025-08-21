from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass

from ...cybozu.dto import Comment


@dataclass(order=True)
class GaroonComment(Comment, metaclass=ABCMeta):
    pass
