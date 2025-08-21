from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass, field

from ..url.dto import KintoneRecordCommentUrl
from ...cybozu.dto import Comment


@dataclass(order=True)
class KintoneComment(Comment, metaclass=ABCMeta):
    pass


@dataclass(order=True)
class KintoneRecordComment(KintoneComment):
    app_id: int = field(compare=False)
    record_id: int = field(compare=False)

    @property
    def url(self) -> KintoneRecordCommentUrl:
        return KintoneRecordCommentUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            app_id=self.app_id,
            record_id=self.record_id,
            comment_id=self.id
        )
