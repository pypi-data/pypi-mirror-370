import logging
from typing import Iterator

import requests

from .dto import Org, Group, User
from .dxo import to_user, to_group, to_org
from ..cybozu.dto import AccessData
from ..cybozu.util import get_headers, get_offset_request, check_response

_DEFAULT_LIMIT: int = 100


def get_users(access_data: AccessData | None = None, is_valid_only: bool = False) -> Iterator[User]:
    logging.info("Get Users")
    if access_data is None:
        access_data = AccessData()
    for user_json in get_offset_request(
            url=f"https://{access_data.host}/v1/users.json",
            headers=get_headers(access_data=access_data),
            params={},
            key="users",
            limit=_DEFAULT_LIMIT):
        if is_valid_only and not user_json.get("valid", True):
            continue
        yield to_user(user_json)


def get_groups(access_data: AccessData | None = None) -> Iterator[Group]:
    logging.info("Get Groups")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/common/docs/user-api/groups/get-groups/
    for group_json in get_offset_request(
            url=f"https://{access_data.host}/v1/groups.json",
            headers=get_headers(access_data=access_data),
            params={},
            key="groups",
            limit=_DEFAULT_LIMIT):
        yield to_group(group_json)


def get_orgs(access_data: AccessData | None = None) -> Iterator[Org]:
    logging.info("Get Organizations")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/common/docs/user-api/organizations/get-organizations/
    for org_json in get_offset_request(
            url=f"https://{access_data.host}/v1/organizations.json",
            headers=get_headers(access_data=access_data),
            params={},
            key="organizations",
            limit=_DEFAULT_LIMIT):
        yield to_org(org_json)


def get_user_codes_by_org_code(org_code: str, access_data: AccessData | None = None) -> set[str]:
    logging.info(f"Get User Codes by Organization Code: {org_code}")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/common/docs/user-api/organizations/get-organizations-users/
    user_codes: set[str] = set([])
    for u in get_offset_request(
            url=f"https://{access_data.host}/v1/organization/users.json",
            headers=get_headers(access_data=access_data),
            params={"code": org_code},
            key="userTitles",
            limit=_DEFAULT_LIMIT):
        user_codes.add(u["user"]["code"])
    return user_codes


def get_user_codes_by_group_code(group_code: str, access_data: AccessData | None = None) -> set[str]:
    logging.info(f"Get User Codes by Group Code: {group_code}")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/common/docs/user-api/groups/get-groups-users/
    user_codes: set[str] = set([])
    for u in get_offset_request(
            url=f"https://{access_data.host}/v1/group/users.json",
            headers=get_headers(access_data=access_data),
            params={"code": group_code},
            key="users",
            limit=_DEFAULT_LIMIT):
        user_codes.add(u["code"])
    return user_codes


def _get(path: str, params: dict | None, access_data: AccessData | None = None) -> dict:
    logging.info(f"GET: {path}" + ("" if params is None else f"?{params}"))
    if access_data is None:
        access_data = AccessData()
    res = requests.get(
        f"https://{access_data.host}/v1/{path}.json",
        headers=get_headers(access_data=access_data, has_body=False),
        params=params
    )
    check_response(res)
    return res.json()


def get_orgs_by_user_code(user_code: str, access_data: AccessData | None = None) -> list[Org]:
    logging.info(f"Get Organizations by User Code: {user_code}")
    if access_data is None:
        access_data = AccessData()
    json_: dict = _get(
        path="user/organizations",
        params={"code": user_code},
        access_data=access_data
    )
    return [to_org(org["organization"]) for org in json_["organizationTitles"]]


def get_groups_by_user_code(user_code: str, access_data: AccessData | None = None) -> list[Group]:
    logging.info(f"Get Groups by User Code: {user_code}")
    if access_data is None:
        access_data = AccessData()
    json_: dict = _get(
        path="user/groups",
        params={"code": user_code},
        access_data=access_data
    )
    return [to_group(group) for group in json_["groups"]]
