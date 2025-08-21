from .dto import Group, Org, User
from ..cybozu.constant import Locales
from ..util import get_str_optional, get_date_optional, get_int_optional, str_to_datetime


def to_user(slash_json: dict) -> User:
    # https://cybozu.dev/ja/common/docs/user-api/overview/data-structure/#user
    return User(
        code=str(slash_json["code"]),
        id=int(slash_json["id"]),
        created_at=str_to_datetime(slash_json["ctime"]),
        updated_at=str_to_datetime(slash_json["mtime"]),
        is_valid=bool(slash_json["valid"]),
        name=str(slash_json["name"].strip()),
        locale=Locales.from_str(slash_json["locale"]),
        timezone=str(slash_json["timezone"]),
        description=get_str_optional(slash_json, "description"),
        mail_address=get_str_optional(slash_json, "email"),
        employee_number=get_str_optional(slash_json, "employee_number"),
        url=get_str_optional(slash_json, "url"),
        birth_date=get_date_optional(slash_json, "birth_date"),
        join_date=get_date_optional(slash_json, "join_date"),
        primary_org_id=get_int_optional(slash_json, "primaryOrganization")
    )


def to_group(group_json: dict) -> Group:
    return Group(
        code=str(group_json["code"]),
        id=int(group_json["id"]),
        name=str(group_json["name"]),
        description=get_str_optional(group_json, "description")
    )


def to_org(org_json: dict) -> Org:
    return Org(
        code=str(org_json["code"]),
        id=int(org_json["id"]),
        name=str(org_json["name"]),
        parent_code=get_str_optional(org_json, "parentCode"),
        description=get_str_optional(org_json, "description")
    )
