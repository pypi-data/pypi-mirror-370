from __future__ import annotations

import logging

from . import dxo
from .dto import Space
from ..util import get, put, post
from ...cybozu.dto import AccessData

_DEFAULT_USER_LIST_LIMIT: int = 11
_DEFAULT_LIST_LIMIT: int = 21


def get_space(space_id: int, access_data: AccessData | None = None) -> Space:
    logging.info(f"Get Space: {space_id}")
    json_: dict = get(
        path="space",
        params={"id": space_id},
        access_data=access_data
    )
    return dxo.to_space(json_)


def update_space_body(space_id: int, body: str, access_data: AccessData | None = None) -> None:
    logging.info(f"Update Space Body: {space_id}")
    put(
        path="space/body",
        json_={
            "id": space_id,
            "body": body
        },
        access_data=access_data
    )


def update_space_members(
        space_id: int,
        admin_user_codes: set[str],
        user_codes: set[str] | None = None,
        group_codes: set[str] | None = None,
        org_codes: set[str] | None = None,
        access_data: AccessData | None = None) -> None:
    if not admin_user_codes:
        raise ValueError("admin_user_codes must not be empty")
    if user_codes is None:
        user_codes = set([])
    if group_codes is None:
        group_codes = set([])
    if org_codes is None:
        org_codes = set([])
    user_codes = user_codes - admin_user_codes
    logging.info(f"Update Space Members: {space_id}")
    put(
        path="space/members",
        json_={
            "id": space_id,
            "members": [
                {
                    "entity": {
                        "type": "USER",
                        "code": code
                    },
                    "isAdmin": True
                } for code in admin_user_codes
            ] + [
                {
                    "entity": {
                        "type": "USER",
                        "code": code
                    },
                    "isAdmin": False
                } for code in user_codes
            ] + [
                {
                    "entity": {
                        "type": "GROUP",
                        "code": code
                    }
                } for code in group_codes
            ] + [
                {
                    "entity": {
                        "type": "ORGANIZATION",
                        "code": code
                    }
                } for code in org_codes
            ]
        },
        access_data=access_data
    )


def create_thread(space_id: int, name: str, access_data: AccessData | None = None) -> int:
    logging.info(f"Create Thread(Official): {name}")
    res: dict = post(
        path="space/thread",
        json_={
            "space": space_id,
            "name": name
        },
        access_data=access_data
    )
    return int(res["id"])


def update_thread(thread_id: int, name: str | None = None, body: str | None = None, access_data: AccessData | None = None) -> None:
    logging.info(f"Update Thread: {thread_id}")
    if name is None and body is None:
        raise ValueError("name and body must not be None at the same time")
    req_json: dict = {"id": thread_id}
    if name is not None:
        req_json["name"] = name
    if body is not None:
        req_json["body"] = body
    put(
        path="space/thread",
        json_=req_json,
        access_data=access_data
    )
