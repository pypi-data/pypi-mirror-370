from __future__ import annotations

import logging

import requests

from ..cybozu.dto import AccessData
from ..cybozu.util import get_headers, check_response


def get(path: str, params: dict | None, app_ids: set[int] | int | None = None, access_data: AccessData | None = None) -> dict:
    logging.info(f"GET: {path}" + ("" if params is None else f"?{params}"))
    if access_data is None:
        access_data = AccessData()
    res = requests.get(
        f"https://{access_data.host}/k/v1/{path}.json",
        headers=get_headers(access_data=access_data, has_body=False, app_ids=app_ids),
        params=params
    )
    check_response(res)
    return res.json()


def post(path: str, json_: dict, app_id: int | None = None, access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> dict:
    logging.info(f"POST: {path}")
    if access_data is None:
        access_data = AccessData()
    app_ids: set[int] = {app_id} if app_id is not None else set([])
    if additional_app_ids:
        app_ids.update(additional_app_ids)
    res = requests.post(
        f"https://{access_data.host}/k/v1/{path}.json",
        headers=get_headers(access_data=access_data, has_body=True, app_ids=app_ids),
        json=json_
    )
    check_response(res)
    return res.json()


def put(path: str, json_: dict, app_id: int | None = None, access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> dict:
    logging.info(f"PUT: {path}")
    if access_data is None:
        access_data = AccessData()
    app_ids: set[int] = {app_id} if app_id is not None else set([])
    if additional_app_ids:
        app_ids.update(additional_app_ids)
    res = requests.put(
        f"https://{access_data.host}/k/v1/{path}.json",
        headers=get_headers(access_data=access_data, has_body=True, app_ids=app_ids),
        json=json_
    )
    check_response(res)
    return res.json()


def delete(path: str, json_: dict | None, app_id: int | None = None, access_data: AccessData | None = None) -> dict:
    logging.info(f"DELETE: {path}")
    if access_data is None:
        access_data = AccessData()
    app_ids: set[int] = {app_id} if app_id is not None else set([])
    res = requests.delete(
        f"https://{access_data.host}/k/v1/{path}.json",
        headers=get_headers(access_data=access_data, has_body=json_ is not None, app_ids=app_ids),
        json=json_
    )
    check_response(res)
    return res.json()
