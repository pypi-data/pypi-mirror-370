from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass

from ...cybozu.dto import CybozuDotComUrl


@dataclass
class KintoneUrl(CybozuDotComUrl, metaclass=ABCMeta):
    @property
    def _product(self) -> str:
        return "k"


@dataclass
class KintoneSpaceUrl(KintoneUrl):
    space_id: int

    @property
    def fragment(self) -> str:
        return f"/space/{self.space_id}"


@dataclass
class KintoneThreadUrl(KintoneSpaceUrl):
    thread_id: int

    @property
    def fragment(self) -> str:
        return f"/space/{self.space_id}/thread/{self.thread_id}"


@dataclass
class KintonePeopleUrl(KintoneUrl):
    user_code: str

    @property
    def fragment(self) -> str:
        return f"/people/user/{self.user_code}"


@dataclass
class KintoneMessageUrl(KintoneUrl):
    user_id1: int
    user_id2: int

    @property
    def fragment(self) -> str:
        return f"/message/{self.user_id1};{self.user_id2}"


@dataclass
class KintoneCommentUrl(KintoneUrl, metaclass=ABCMeta):
    comment_id: int


@dataclass
class KintoneChildCommentUrl(KintoneCommentUrl, metaclass=ABCMeta):
    parent_comment_id: int


@dataclass
class KintoneThreadCommentUrl(KintoneThreadUrl, KintoneCommentUrl):
    @property
    def fragment(self) -> str:
        return f"/space/{self.space_id}/thread/{self.thread_id}/{self.comment_id}"


@dataclass
class KintoneThreadChildCommentUrl(KintoneThreadUrl, KintoneChildCommentUrl):
    @property
    def fragment(self) -> str:
        return f"/space/{self.space_id}/thread/{self.thread_id}/{self.parent_comment_id}/{self.comment_id}"


@dataclass
class KintonePeopleCommentUrl(KintonePeopleUrl, KintoneCommentUrl):
    @property
    def fragment(self) -> str:
        return f"/people/user/{self.user_code}/{self.comment_id}"


@dataclass
class KintonePeopleChildCommentUrl(KintonePeopleUrl, KintoneChildCommentUrl):
    @property
    def fragment(self) -> str:
        return f"/people/user/{self.user_code}/{self.parent_comment_id}/{self.comment_id}"


@dataclass
class KintoneMessageCommentUrl(KintoneMessageUrl, KintoneCommentUrl):
    @property
    def fragment(self) -> str:
        return f"/message/{self.user_id1};{self.user_id2}/{self.comment_id}"


@dataclass
class KintoneAppUrl(KintoneUrl):
    app_id: int

    @property
    def path(self) -> str:
        return f"{self.app_id}/"


@dataclass
class KintoneRecordUrl(KintoneAppUrl):
    record_id: int

    @property
    def path(self) -> str:
        return f"{self.app_id}/show"

    @property
    def fragment(self) -> str:
        return f"record={self.record_id}"


@dataclass
class KintoneRecordCommentUrl(KintoneRecordUrl, KintoneCommentUrl):
    @property
    def fragment(self) -> str:
        return f"record={self.record_id}&comment={self.comment_id}"


@dataclass
class KintoneNotifyUrl(KintoneUrl):
    notify_id: int
    group_key: str

    @property
    def fragment(self) -> str:
        return f"/ntf/all/k/space/{self.group_key}/{self.notify_id}"
