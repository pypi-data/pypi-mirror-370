from .dto import KintoneApp, KintoneAppSetting, KintoneAppField, KintoneAppEntity
from ..constant import AppFieldTypes, EntityTypes
from ...util import kintone_str_to_datetime, json_get_optional, get_int_optional


def to_app(app_json: dict) -> KintoneApp:
    return KintoneApp(
        id=int(str(app_json.get("appId", app_json.get("id")))),
        name=str(app_json["name"]),
        creator_code=json_get_optional(app_json, "creator", "code"),
        creator_name=json_get_optional(app_json, "creator", "name"),
        last_modifier_code=json_get_optional(app_json, "modifier", "code"),
        last_modifier_name=json_get_optional(app_json, "modifier", "name"),
        created_at=kintone_str_to_datetime(app_json["createdAt"]),
        modified_at=kintone_str_to_datetime(app_json["modifiedAt"]),
        space_id=get_int_optional(app_json, "spaceId"),
        thread_id=get_int_optional(app_json, "threadId"),
        description=app_json.get("description", None)
    )


def to_app_setting(app_setting_json: dict) -> KintoneAppSetting:
    return KintoneAppSetting(
        name=app_setting_json["name"],
        description=app_setting_json.get("description", None),
        title_field=json_get_optional(app_setting_json, "titleField", "code"),
        enable_thumbnails=app_setting_json["enableThumbnails"],
        enable_bulk_deletion=app_setting_json["enableBulkDeletion"],
        enable_comments=app_setting_json["enableComments"],
        revision=app_setting_json["revision"]
    )


def to_app_field(property_json: dict) -> KintoneAppField:
    field_type: AppFieldTypes = AppFieldTypes(property_json["type"])
    code: str = property_json["code"]
    label: str = property_json["label"]
    required: bool | None = property_json.get("required", None)
    has_unique_constraint: bool | None = property_json.get("unique", None)
    max_value: int | None = property_json.get("maxValue", property_json.get("maxLength", None))
    min_value: int | None = property_json.get("minValue", property_json.get("minLength", None))
    default_value: str | int | set | None = property_json.get("defaultValue", None)
    default_now_value: bool = property_json.get("defaultNowValue", False)
    options: list[str] | None = None
    if "options" in property_json:
        options = [o["label"] for o in property_json["options"].values()]
    entities: list[KintoneAppEntity] | None = None
    if "entities" in property_json:
        entities = [KintoneAppEntity(code=e["code"], type=EntityTypes(e["type"])) for e in property_json["entities"]]
    subtable: list[KintoneAppField] | None = None
    if field_type == AppFieldTypes.SUBTABLE:
        subtable = [to_app_field(f) for f in property_json["fields"].values()]
    return KintoneAppField(
        type=field_type,
        code=code,
        label=label,
        required=required,
        has_unique_constraint=has_unique_constraint,
        max_value=max_value,
        min_value=min_value,
        default_value=default_value,
        default_now_value=default_now_value,
        options=options,
        entities=entities,
        subtable=subtable
    )
