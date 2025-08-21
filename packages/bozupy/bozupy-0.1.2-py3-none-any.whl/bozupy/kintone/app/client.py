from __future__ import annotations

import logging
from typing import Iterator

import requests

from . import dxo
from .dto import KintoneAppSetting, KintoneAppField, KintoneApp
from .graph import KintoneGraphBuilder
from ..constant import AppFieldTypes
from ..record.query import KintoneQueryBuilder
from ..util import get, post, put
from ...cybozu.dto import AccessData
from ...cybozu.util import get_headers, check_response

_DEFAULT_LIMIT: int = 100


def get_app_setting(app_id: int, access_data: AccessData | None = None) -> KintoneAppSetting:
    logging.info(f"Get App Setting: {app_id}")
    # https://cybozu.dev/ja/kintone/docs/rest-api/apps/settings/get-general-settings/
    params: dict[str, int | str] = {"app": app_id, "lang": "ja"}
    return dxo.to_app_setting(get("app/settings", params, app_id, access_data))


def get_app_fields(app_id: int, use_preview: bool = False, access_data: AccessData | None = None) -> list[KintoneAppField]:
    logging.info(f"Get App Fields: {app_id}")
    # https://cybozu.dev/ja/kintone/docs/rest-api/apps/form/get-form-fields/
    try:
        fields_json: dict = get("app/form/fields", {"app": app_id}, app_id, access_data)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 403 and use_preview:
            fields_json = get("preview/app/form/fields", {"app": app_id}, app_id, access_data)
        else:
            raise e
    return [dxo.to_app_field(field_json) for field_json in fields_json["properties"].values()]


def get_app_views(app_id: int, access_data: AccessData | None = None) -> dict:
    logging.info(f"Get App Views: {app_id}")
    # TODO: dataclassに変換する
    return get("app/views", {"app": app_id}, app_id, access_data)


def get_app_process_conf(app_id: int, access_data: AccessData | None = None) -> dict:
    logging.info(f"Get App Process Conf: {app_id}")
    # TODO: dataclassに変換する
    return get("app/status", {"app": app_id}, app_id, access_data)


def create_preview_app(app_name: str, access_data: AccessData | None = None) -> int:
    logging.info(f"Create Preview App: {app_name}")
    res: dict = post("preview/app", {"name": app_name}, None, access_data)
    return int(res["app"])


def deploy_app(app_id: int, access_data: AccessData | None = None) -> None:
    logging.info(f"Deploy App: {app_id}")
    post("preview/app/deploy", {"apps": [{"app": app_id}]}, app_id, access_data)


def update_app_name(app_id: int, app_name: str, access_data: AccessData | None = None) -> None:
    logging.info(f"Update App Name: {app_id}")
    put("preview/app/settings", {"app": app_id, "name": app_name}, app_id, access_data)
    deploy_app(app_id, access_data)


def add_field_to_preview_app(app_id: int, type_: AppFieldTypes, code: str, label: str, access_data: AccessData | None = None, options: set[str] | None = None) -> None:
    logging.info(f"Add Field to Preview App: {app_id}")
    body: dict = {
        "app": app_id,
        "properties": {
            code: {
                "code": code,
                "label": label,
                "type": type_.value,
            }
        }
    }
    if options:
        body["properties"][code]["options"] = {o: {"label": o, "index": i} for i, o in enumerate(options)}
    post("preview/app/form/fields", json_=body, app_id=app_id, access_data=access_data)


def get_app(app_id: int, access_data: AccessData | None = None) -> KintoneApp:
    logging.info(f"Get App: {app_id}")
    # https://cybozu.dev/ja/kintone/docs/rest-api/apps/get-app/
    app_json: dict = get("app", {"id": app_id}, app_id, access_data)
    return dxo.to_app(app_json)


def get_apps(access_data: AccessData | None = None, limit: int = _DEFAULT_LIMIT) -> Iterator[KintoneApp]:
    logging.info("Get Apps")
    if limit <= 0:
        limit = _DEFAULT_LIMIT
    offset: int = 0
    while True:
        params: dict[str, int] = {"limit": limit, "offset": offset}
        app_jsons: list[dict] = get("apps", params=params, app_ids=None, access_data=access_data)["apps"]
        for app_json in app_jsons:
            yield dxo.to_app(app_json)
        if len(app_jsons) < limit:
            break
        offset += len(app_jsons)


def get_app_acl(app_id: int, access_data: AccessData | None = None) -> list[dict]:
    logging.info(f"Get App ACL: {app_id}")
    if access_data is None:
        access_data = AccessData()
    params: dict[str, int] = {"app": app_id}
    res: requests.Response = requests.get(
        f"https://{access_data.host}/k/v1/app/acl.json",
        headers=get_headers(access_data=access_data, has_body=False, app_ids=app_id),
        params=params
    )
    if res.status_code == 403 and "権限がありません" in res.json().get("message", ""):
        return []
    elif res.status_code == 520 and "ゲストスペース" in res.json().get("message", ""):
        return []
    check_response(res)
    # TODO: dataclassに変換する
    return res.json()["rights"]


def upsert_graph(app_id: int, graph_id: int, graph: KintoneGraphBuilder, query: KintoneQueryBuilder | None = None, access_data: AccessData | None = None) -> None:
    logging.info(f"Upsert Graph: {app_id} - {graph_id}")
    graph_json: dict = graph.build()
    graph_json["index"] = graph_id
    graph_json["periodicReport"] = None  # TODO
    if query is not None:
        graph_json["filterCond"] = query.build()
    else:
        graph_json["filterCond"] = ""
    put("preview/app/reports", {
        "app": app_id,
        "reports": {
            graph.name: graph_json
        }
    }, app_id=app_id, access_data=access_data)
    deploy_app(app_id, access_data)
