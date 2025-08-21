from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import requests

from . import dxo
from .query import KintoneQueryBuilder
from ...cybozu.dto import AccessData
from ...cybozu.util import get_headers, check_response
from .dto import KintoneRecord, KintoneRecordSingleLineTextField
from ..util import get, post, delete, put

_DEFAULT_GET_RECORD_LIMIT: int = 500
_DEFAULT_LIMIT: int = 100
_DEFAULT_RECORD_CHANGE_LIMIT: int = 10


def get_records_by_offset(app_id: int,
                          query: KintoneQueryBuilder | None = None,
                          access_data: AccessData | None = None) -> Iterator[KintoneRecord]:
    logging.info(f"Get Records by Offset: {app_id}")
    params: dict = {"app": app_id}
    query_: KintoneQueryBuilder = KintoneQueryBuilder() if query is None else query
    # TODO: protectedメンバにアクセスしているので修正する
    # noinspection PyProtectedMember
    if query_._fields:
        # レコードIDは必ず取得する
        query_.field("$id")
        # noinspection PyProtectedMember
        params["fields"] = ",".join([str(f) for f in sorted(query_._fields)])
    query_str: str = query_.build()
    if query_str:
        params["query"] = query_str
    records: list[dict] = get("records", params, app_id, access_data)["records"]
    for record_dict in records:
        yield dxo.to_record(record_dict, app_id, record_dict["$id"]["value"])


def get_records(
        app_id: int,
        query: KintoneQueryBuilder | None = None,
        access_data: AccessData | None = None) -> Iterator[KintoneRecord]:
    logging.info(f"Get Records: {app_id}")
    params: dict = {"app": app_id, "size": _DEFAULT_GET_RECORD_LIMIT}
    if query is not None:
        params["query"] = query.build(is_cursor=True)
        # noinspection PyProtectedMember
        if query._fields:
            # レコードIDは必ず取得する
            query.field("$id")
            # noinspection PyProtectedMember
            params["fields"] = ",".join([str(f) for f in sorted(query._fields)])
    cursor: str = post("records/cursor", params, app_id, access_data)["id"]
    is_cursor_deleted: bool = False
    try:
        while True:
            result: dict = get("records/cursor", {"id": cursor}, app_id, access_data)
            for record_dict in result["records"]:
                yield dxo.to_record(record_dict, app_id, record_dict["$id"]["value"])
            if not result["next"]:
                is_cursor_deleted = True
                break
    finally:
        if not is_cursor_deleted:
            try:
                delete("records/cursor", {"id": cursor}, app_id, access_data)
            except Exception:
                pass


def get_record(app_id: int, record_id: int, access_data: AccessData | None = None) -> KintoneRecord:
    logging.info(f"Get Record: {app_id}, {record_id}")
    return dxo.to_record(get("record", {"app": app_id, "id": record_id}, app_id, access_data)["record"], app_id, record_id)


def add_record(record: KintoneRecord, access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> int:
    logging.info(f"Add Record: {record.app_id}")
    if record.id is not None:
        raise ValueError("record id must be None")
    record_id: int = add_record_raw(record.app_id, dxo.to_dict(record, True), access_data, additional_app_ids)
    record.id = record_id
    return record_id


def add_record_raw(app_id: int, record: dict, access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> int:
    logging.info(f"Add Record Raw: {app_id}")
    res: dict = post("record", {"app": app_id, "record": record}, app_id, access_data, additional_app_ids)
    return int(res["id"])


def add_records(records: list[KintoneRecord], access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> list[int]:
    logging.info("Add Records")
    app_ids: set[int] = {r.app_id for r in records}
    if len(app_ids) != 1:
        raise ValueError("all records must be in the same app")
    for r in records:
        if r.id is not None:
            raise ValueError("record id must be None")
    app_id: int = app_ids.pop()
    record_ids: list[int] = add_records_raw(app_id, [dxo.to_dict(record, True) for record in records], access_data, additional_app_ids)
    for i, record in enumerate(records):
        record.id = record_ids[i]
    return record_ids


def add_records_raw(app_id: int, records: list[dict], access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> list[int]:
    logging.info("Add Records Raw")
    record_ids: list[int] = []
    while len(records) != 0:
        res: dict = post(
            "records",
            {
                "app": app_id,
                "records": [r for r in records[:_DEFAULT_LIMIT]]
            },
            app_id,
            access_data,
            additional_app_ids
        )
        record_ids.extend([int(id_) for id_ in res["ids"]])
        records = records[_DEFAULT_LIMIT:]
    return record_ids


def update_record(record: KintoneRecord, access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> None:
    logging.info(f"Update Record: {record.app_id}, {record.id}")
    if record.id is None:
        raise ValueError("record id is required")
    return update_record_raw(record.app_id, record.id, dxo.to_dict(record, True), access_data, additional_app_ids)


def update_record_raw(app_id: int, record_id: int, record: dict, access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> None:
    logging.info(f"Update Record Raw: {app_id}, {record_id}")
    put("record", {"app": app_id, "id": record_id, "record": record}, app_id, access_data, additional_app_ids)


def update_records(records: list[KintoneRecord], access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> None:
    logging.info("Update Records")
    app_ids: set[int] = {r.app_id for r in records}
    if len(app_ids) != 1:
        raise ValueError("all records must be in the same app")
    record_ids: set[int] = set([])
    raw_records: list[tuple[int, dict]] = []
    for r in records:
        if r.id is None:
            raise ValueError("record id is required")
        record_ids.add(r.id)
        raw_records.append((r.id, dxo.to_dict(r, True)))
    if len(record_ids) != len(records):
        raise ValueError("all records must have unique id")
    app_id: int = app_ids.pop()
    update_records_raw(app_id, raw_records, access_data, additional_app_ids)


def update_records_raw(app_id: int, records: list[tuple[int, dict]], access_data: AccessData | None = None, additional_app_ids: set[int] | None = None) -> None:
    logging.info("Update Records Raw")
    while len(records) != 0:
        put("records", {"app": app_id, "records": [{"id": record_id, "record": record} for record_id, record in records[:_DEFAULT_LIMIT]]}, app_id, access_data, additional_app_ids)
        records = records[_DEFAULT_LIMIT:]


def upsert_record(record: KintoneRecord, key: str, value: str | int, access_data: AccessData | None = None) -> int:
    logging.info(f"Upsert Record: {record.app_id}, {key}, {value}")
    if record.id is not None:
        raise ValueError("record id must be None")
    current_record: KintoneRecord | None = None
    current_records: list[KintoneRecord] = [r for r in get_records_by_offset(record.app_id, access_data=access_data, query=KintoneQueryBuilder().limit(1).equal(key, value, KintoneRecordSingleLineTextField).field("$id"))]
    if len(current_records) == 1:
        current_record = current_records[0]
    elif len(current_records) > 1:
        raise RuntimeError(f"unexpected record count: {len(current_records)}, {key=}, {value=}")
    if current_record is not None and current_record.id is not None:
        record.id = current_record.id
        update_record(record=record, access_data=access_data)
        return current_record.id
    else:
        return add_record(record=record, access_data=access_data)


def delete_records(app_id: int, record_ids: set[int], access_data: AccessData | None = None) -> None:
    logging.info(f"Delete Records: {app_id}")
    record_ids_: list[int] = list(record_ids)
    while record_ids_:
        delete("records", {"app": app_id, "ids": record_ids_[:_DEFAULT_LIMIT]}, app_id, access_data)
        record_ids_ = record_ids_[_DEFAULT_LIMIT:]


def upload_file(app_id: int, filename: str, path: Path, content_type: str, access_data: AccessData | None = None) -> str:
    logging.info(f"Upload File: {app_id}")
    if access_data is None:
        access_data = AccessData()
    headers: dict = get_headers(access_data=access_data, has_body=True, app_ids=app_id)
    # 自動付与されるContent-Typeを利用しないとboundaryがつかない
    headers.pop("Content-Type")
    with path.open("rb") as f:
        res: requests.Response = requests.post(
            f"https://{access_data.host}/k/v1/file.json",
            headers=headers,
            files={"file": (filename, f, content_type)}
        )
    check_response(res)
    return res.json()["fileKey"]


def download_file(file_key: str, path: Path, app_id: int | None = None, access_data: AccessData | None = None) -> None:
    logging.info(f"Download File: {file_key}")
    if access_data is None:
        access_data = AccessData()
    headers: dict = get_headers(access_data=access_data, has_body=False, app_ids=app_id)
    with path.open("wb") as f:
        res: requests.Response = requests.get(
            f"https://{access_data.host}/k/v1/file.json",
            headers=headers,
            params={"fileKey": file_key}
        )
        check_response(res, is_plain=True)
        f.write(res.content)


def update_record_assignees(app_id: int, record_id: int, assignees: set[str], access_data: AccessData | None = None) -> None:
    logging.info(f"Update Record Assignees: {app_id}, {record_id}")
    if len(assignees) > 100:
        raise ValueError("assignees must be less than or equal to 100")
    put("record/assignees", {"app": app_id, "id": record_id, "assignees": list(assignees)}, app_id, access_data)


def update_record_status(app_id: int, record_id: int, action: str, assignee: str | None = None, access_data: AccessData | None = None) -> None:
    logging.info(f"Update Record Status: {app_id}, {record_id}")
    json_: dict = {"app": app_id, "id": record_id, "action": action}
    if assignee is not None:
        json_["assignee"] = assignee
    put("record/status", json_, app_id, access_data)
