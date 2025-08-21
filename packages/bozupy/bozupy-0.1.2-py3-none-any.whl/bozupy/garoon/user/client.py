import logging
from typing import Iterator

import requests

from ...cybozu.dto import AccessData
from ...cybozu.util import get_headers, check_response


_DEFAULT_LIMIT: int = 100


def get_user_code_and_garoon_ids(access_data: AccessData | None = None) -> Iterator[tuple[str, int]]:
    logging.info("Get User Code and Garoon IDs")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/garoon/docs/rest-api/base/get-users/
    params: dict = {"size": _DEFAULT_LIMIT}
    offset: int = 0
    while True:
        params["offset"] = offset
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/base/users",
            headers=get_headers(access_data=access_data),
            params=params
        )
        check_response(res)
        result: list[dict] = res.json()["users"]
        for user in result:
            yield user["code"], int(user["id"])
        if len(result) < _DEFAULT_LIMIT:
            break
        offset += len(result)


def get_code_garoon_id_map(access_data: AccessData | None = None) -> dict[str, int]:
    logging.info("Get Code Garoon ID Map")
    return {code: id_ for code, id_ in get_user_code_and_garoon_ids(access_data)}


def get_garoon_id_by_code(code: str, access_data: AccessData | None = None) -> int | None:
    logging.info(f"Get Garoon ID by Code: {code}")
    for user_code, id_ in get_user_code_and_garoon_ids(access_data):
        if user_code == code:
            return id_
    return None
