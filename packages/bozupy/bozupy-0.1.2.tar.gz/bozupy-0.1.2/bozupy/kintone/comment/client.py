from __future__ import annotations

import logging

from . import dxo
from .dto import KintoneRecordComment
from ..util import post, get
from ...cybozu.dto import AccessData

_DEFAULT_LIST_LIMIT: int = 21
_DEFAULT_CHILD_COMMENT_LIMIT: int = 7
_DEFAULT_GET_RECORD_COMMENT_LIMIT: int = 10


def get_record_comments(app_id: int, record_id: int, access_data: AccessData | None = None) -> list[KintoneRecordComment]:
    if access_data is None:
        access_data = AccessData()
    logging.info(f"Get Record Comments by official API: {app_id}, {record_id}")
    comments: list[KintoneRecordComment] = []
    offset: int = 0
    while True:
        json_: dict = get("record/comments", {
            "app": app_id,
            "record": record_id,
            "order": "asc",
            "offset": offset,
            "limit": _DEFAULT_GET_RECORD_COMMENT_LIMIT
        }, app_ids=app_id, access_data=access_data)
        for comment_json in json_["comments"]:
            comment: KintoneRecordComment = dxo.to_record_comment(comment_json, app_id, record_id, access_data.subdomain, access_data.is_dev)
            comments.append(comment)
        if len(json_["comments"]) != _DEFAULT_GET_RECORD_COMMENT_LIMIT:
            break
        offset += _DEFAULT_GET_RECORD_COMMENT_LIMIT
    return comments


def post_record_comment(app_id: int, record_id: int, comment: str, mention_codes: set[str] | None = None, access_data: AccessData | None = None) -> int:
    logging.info(f"Post Record Comment: {app_id}, {record_id}")
    if not mention_codes:
        mention_codes_: set[str] = set([])
    else:
        mention_codes_ = mention_codes
    res: dict = post("record/comment", {
        "app": app_id,
        "record": record_id,
        "comment": {
            "text": comment,
            "mentions": [
                {"type": "USER", "code": code}
                for code in mention_codes_
            ]
        },
    }, app_id, access_data)
    return int(res["id"])


def post_thread_comment(
        space_id: int,
        thread_id: int,
        comment: str,
        mention_codes: set[str] | None = None,
        mention_group_codes: set[str] | None = None,
        mention_org_codes: set[str] | None = None,
        file_keys: set[str] | None = None,
        access_data: AccessData | None = None) -> int:
    json_: dict = post(
        path="space/thread/comment",
        access_data=access_data,
        json_={
            "space": space_id,
            "thread": thread_id,
            "comment": {
                "text": comment,
                "mentions": [
                    {"type": "USER", "code": code}
                    for code in mention_codes or []
                ] + [
                    {"type": "GROUP", "code": code}
                    for code in mention_group_codes or []
                ] + [
                    {"type": "ORGANIZATION", "code": code}
                    for code in mention_org_codes or []
                ]
            },
            "files": [
                {"fileKey": file_key}
                for file_key in file_keys or []
            ]
        }
    )
    return int(json_["id"])
