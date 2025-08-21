from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..constant import AppFieldTypes, EntityTypes


@dataclass
class KintoneApp:
    id: int
    name: str
    creator_code: str | None
    last_modifier_code: str | None
    creator_name: str | None
    last_modifier_name: str | None
    created_at: datetime
    modified_at: datetime
    space_id: int | None
    thread_id: int | None
    description: str | None


@dataclass
class KintoneAppSetting:
    name: str
    description: str | None
    title_field: str | None
    enable_thumbnails: bool
    enable_bulk_deletion: bool
    enable_comments: bool
    revision: int


@dataclass
class KintoneAppEntity:
    code: str
    type: EntityTypes


# TODO:
# @dataclass
# class KintoneAppReference:
#     app_id: int
#     code: str

# @dataclass
# class KintoneAppLookup:
#     app_id: int
#     code: str


@dataclass
class KintoneAppField:
    type: AppFieldTypes
    code: str
    label: str
    required: bool | None
    has_unique_constraint: bool | None
    max_value: int | None
    min_value: int | None
    default_value: str | int | set | None
    default_now_value: bool | None
    options: list[str] | None
    entities: list[KintoneAppEntity] | None
    # TODO:
    # reference: KintoneAppReference | None
    # lookup: KintoneAppLookup | None
    subtable: list[KintoneAppField] | None
