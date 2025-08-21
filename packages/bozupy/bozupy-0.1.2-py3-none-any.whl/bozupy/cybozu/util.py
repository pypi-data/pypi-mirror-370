import base64
import logging
from typing import Iterator

import requests

from .dto import AccessData
from ..exception import LoginRequired, AccessForbidden, RateLimitExceeded, RequestNotSuccess, APIError, NoJsonResponse
from ..setting import USER_AGENT
from ..util import debug_response_print


def get_headers(access_data: AccessData | None, has_body: bool = False, app_ids: set[int] | int | None = None) -> dict[str, str]:
    if access_data is None:
        access_data = AccessData()
    headers: dict[str, str] = {
        "Host": f"{access_data.host}:443",
        "User-Agent": USER_AGENT
    }
    if has_body:
        headers["Content-Type"] = "application/json"
    tokens: set[str] = set([])
    if app_ids is None:
        app_ids = set([])
    elif isinstance(app_ids, int):
        app_ids = {app_ids}
    for app_id in app_ids:
        if app_id in access_data.app_tokens:
            tokens.add(access_data.app_tokens[app_id])
    if tokens and app_ids and len(tokens) == len(app_ids):
        headers["X-Cybozu-API-Token"] = ",".join(sorted(tokens))
        logging.info("Use API Token")
    elif access_data.has_auth:
        headers["X-Cybozu-Authorization"] = base64.b64encode(
            f"{access_data.username}:{access_data.password}".encode()).decode()
        logging.info("Use Password")
    else:
        raise ValueError("No Auth Data")
    return headers


def check_response(res: requests.Response, is_plain: bool = False):
    debug_response_print(res)
    # エラーを出し分けたいのでres.raise_for_status()は使わない
    if res.status_code <= 299:
        if is_plain:
            return
        elif "application/json" not in res.headers.get("Content-Type", ""):
            raise NoJsonResponse(res)
        try:
            res_json: dict | list = res.json()
        except ValueError:
            raise NoJsonResponse(res)
        if not isinstance(res_json, dict) or "success" not in res_json or res_json["success"]:
            return
        else:
            raise RequestNotSuccess(res)
    elif res.status_code == 401:
        raise LoginRequired(res)
    elif res.status_code == 302 and "/login" in res.headers.get("Location", ""):
        raise LoginRequired(res)
    elif res.status_code == 403:
        raise AccessForbidden(res)
    elif res.status_code == 429:
        raise RateLimitExceeded(res)
    elif res.status_code == 502 and "一時的な過負荷かメンテナンス" in res.text:
        raise RateLimitExceeded(res)
    elif res.status_code == 520:
        raise APIError(res)
    raise requests.HTTPError(response=res)


def get_offset_request(url: str, headers: dict, params: dict, key: str, limit: int) -> Iterator[dict]:
    offset: int = 0
    params["size"] = limit
    while True:
        ps: dict = params.copy()
        ps["offset"] = offset
        res: requests.Response = requests.get(url, headers=headers, params=ps)
        check_response(res)
        result: list[dict] = res.json()[key]
        yield from result
        if len(result) < limit:
            break
        offset += len(result)
