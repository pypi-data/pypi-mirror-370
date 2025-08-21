import logging
from typing import Any, Type

from .dto import KintoneRecord, KintoneRecordField, KintoneRecordIDField, \
    KintoneRecordRevisionField, KintoneRecordCreatorField, KintoneRecordCreatedTimeField, KintoneRecordModifierField, \
    KintoneRecordUpdatedTimeField, KintoneRecordSingleLineTextField, KintoneRecordMultiLineTextField, \
    KintoneRecordRichTextField, KintoneRecordNumberField, KintoneRecordCalcField, KintoneRecordCheckBoxField, \
    KintoneRecordRadioButtonField, KintoneRecordMultiSelectField, KintoneRecordDropDownField, \
    KintoneRecordUserSelectField, KintoneRecordOrgSelectField, KintoneRecordGroupSelectField, KintoneRecordDateField, \
    KintoneRecordTimeField, KintoneRecordDateTimeField, KintoneRecordFileField, KintoneRecordLinkField, \
    KintoneRecordSubtableField, KintoneRecordCategoryField, KintoneRecordStatusField, \
    KintoneRecordAssigneeField, KintoneRecordCodeField

_field_classes: list[Type[KintoneRecordField]] = [
    KintoneRecordCodeField,
    KintoneRecordIDField,
    KintoneRecordRevisionField,
    KintoneRecordCreatorField,
    KintoneRecordCreatedTimeField,
    KintoneRecordModifierField,
    KintoneRecordUpdatedTimeField,
    KintoneRecordSingleLineTextField,
    KintoneRecordMultiLineTextField,
    KintoneRecordRichTextField,
    KintoneRecordNumberField,
    KintoneRecordCalcField,
    KintoneRecordCheckBoxField,
    KintoneRecordRadioButtonField,
    KintoneRecordMultiSelectField,
    KintoneRecordDropDownField,
    KintoneRecordUserSelectField,
    KintoneRecordOrgSelectField,
    KintoneRecordGroupSelectField,
    KintoneRecordDateField,
    KintoneRecordTimeField,
    KintoneRecordDateTimeField,
    KintoneRecordLinkField,
    KintoneRecordFileField,
    KintoneRecordSubtableField,
    KintoneRecordCategoryField,
    KintoneRecordStatusField,
    KintoneRecordAssigneeField
]
_FIELD_TYPE_TO_FIELD_CLASS: dict[str, Type[KintoneRecordField]] = {
    class_.field_type(): class_
    for class_ in _field_classes
}


def to_record(record_json: dict, app_id: int, record_id: int) -> KintoneRecord:
    record: KintoneRecord = KintoneRecord(app_id=app_id, id=record_id)
    for code, value_json in record_json.items():
        value: Any = value_json["value"]
        type_: str = value_json["type"]
        if type_ not in _FIELD_TYPE_TO_FIELD_CLASS:
            raise ValueError(f"unknown field type: {type_}")
        try:
            if type_ == "SUBTABLE":
                # これだけvalueを書き換えてやる必要がある
                if not isinstance(value, list):
                    raise ValueError(f"invalid subtable value: {value}")
                rows: list[tuple[int, list[KintoneRecordField]]] = []
                for row_json in value:
                    row_id: int = int(row_json["id"])
                    fields: list[KintoneRecordField] = []
                    for field_code, field_value_json in row_json["value"].items():
                        field_value: Any = field_value_json["value"]
                        field_type: str = field_value_json["type"]
                        field_class: Type[KintoneRecordField] = _FIELD_TYPE_TO_FIELD_CLASS[field_type]
                        fields.append(field_class.from_json(field_code, field_value))
                    rows.append((row_id, fields))
                value = rows
            field_class = _FIELD_TYPE_TO_FIELD_CLASS[type_]
            record.set_field(field_class.from_json(code, value))
        except Exception as e:
            logging.error(f"failed to parse field: {code} value: {value} type: {value_json['type']}", exc_info=e)
    return record


def to_dict(record: KintoneRecord, is_update: bool = False) -> dict:
    return {
        field.code: field.to_json()
        for field in record.fields.values() if is_update and field.updatable()
    }
