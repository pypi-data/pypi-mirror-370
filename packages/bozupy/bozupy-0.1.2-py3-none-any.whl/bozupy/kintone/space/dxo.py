from datetime import datetime

from .dto import Space
from ...util import str_to_datetime


def to_space(space_info_json: dict) -> Space:
    creator_code: str | None = None
    modifier_code: str | None = None
    if "creator" in space_info_json and space_info_json["creator"] is not None and "code" in space_info_json["creator"]:
        creator_code = str(space_info_json["creator"]["code"])
    if "modifier" in space_info_json and space_info_json["modifier"] is not None and "code" in space_info_json["modifier"]:
        modifier_code = str(space_info_json["modifier"]["code"])
    return Space(
        id=int(space_info_json["id"]),
        default_thread_id=int(space_info_json["defaultThread"]),
        creator_code=creator_code,
        modifier_code=modifier_code,
        created_at=str_to_datetime(space_info_json["createdAt"]) if "createdAt" in space_info_json else datetime.now(),
        modified_at=str_to_datetime(space_info_json["modifiedAt"]) if "modifiedAt" in space_info_json else datetime.now(),
        body=str(space_info_json["body"]),
        name=str(space_info_json["name"])
    )
