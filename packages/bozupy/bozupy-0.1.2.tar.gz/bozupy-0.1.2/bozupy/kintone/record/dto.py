from __future__ import annotations

from abc import abstractmethod, ABCMeta
from dataclasses import dataclass, field
from datetime import datetime, date, time, timezone, timedelta
from typing import TypeVar, Generic, Any, Type

from lxml import html

from ...util import datetime_to_kintone_str, kintone_str_to_datetime, date_to_kintone_str, time_to_kintone_str, \
    str_to_time, str_to_date

# https://cybozu.dev/ja/kintone/docs/overview/field-types/

_T = TypeVar("_T")


@dataclass
class KintoneRecordField(Generic[_T], metaclass=ABCMeta):
    code: str
    value: _T

    def to_json(self) -> dict:
        return {"value": self.value}

    @classmethod
    @abstractmethod
    def field_type(cls) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_json(cls, code: str, value: Any) -> KintoneRecordField[_T]:
        raise NotImplementedError()

    @classmethod
    def updatable(cls) -> bool:
        return True


@dataclass
class _KintoneRecordIntField(KintoneRecordField[int], metaclass=ABCMeta):
    def to_json(self) -> dict:
        return {"value": str(self.value)}

    @classmethod
    def from_json(cls, code: str, value: int) -> _KintoneRecordIntField:
        return cls(code, int(value))


@dataclass
class _KintoneRecordStrField(KintoneRecordField[str], metaclass=ABCMeta):
    @classmethod
    def from_json(cls, code: str, value: str) -> _KintoneRecordStrField:
        return cls(code, str(value))


@dataclass
class _KintoneRecordUserField(KintoneRecordField[str], metaclass=ABCMeta):
    def to_json(self) -> dict:
        return {"value": {"code": self.value}}

    @classmethod
    def from_json(cls, code: str, value: dict[str, str]) -> _KintoneRecordUserField:
        return cls(code, value["code"])


@dataclass
class _KintoneRecordOptionalStrField(KintoneRecordField[str | None], metaclass=ABCMeta):
    @classmethod
    def from_json(cls, code: str, value: Any) -> _KintoneRecordOptionalStrField:
        if not value:
            return cls(code, None)
        return cls(code, str(value))


@dataclass
class _KintoneRecordDatetimeField(KintoneRecordField[datetime], metaclass=ABCMeta):
    def to_json(self) -> dict:
        v: datetime = (self.value - timedelta(hours=9)).replace(tzinfo=timezone.utc)
        return {"value": datetime_to_kintone_str(v)}

    @classmethod
    def from_json(cls, code: str, value: str) -> _KintoneRecordDatetimeField:
        return cls(code, kintone_str_to_datetime(value))


@dataclass
class _KintoneRecordSetField(KintoneRecordField[set[str]], metaclass=ABCMeta):
    def to_json(self) -> dict:
        return {"value": list(sorted(self.value))}

    @classmethod
    def from_json(cls, code: str, value: list) -> _KintoneRecordSetField:
        return cls(code, set(value))


@dataclass
class _KintoneRecordCodeSelectField(KintoneRecordField[set[str]], metaclass=ABCMeta):
    def to_json(self) -> dict:
        return {"value": [{"code": code} for code in sorted(self.value)]}

    @classmethod
    def from_json(cls, code: str, value: list[dict[str, str]]) -> _KintoneRecordCodeSelectField:
        return cls(code, {item["code"] for item in value})


@dataclass
class KintoneRecordCodeField(_KintoneRecordStrField):
    @classmethod
    def field_type(cls) -> str:
        return "RECORD_NUMBER"

    @property
    def has_app_code(self) -> bool:
        return "-" in self.value

    @property
    def app_code(self) -> str:
        if not self.has_app_code:
            raise ValueError("This record ID does not have an app code.")
        return self.value.split("-")[0]

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordIDField(_KintoneRecordIntField):
    @classmethod
    def field_type(cls) -> str:
        return "__ID__"

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordRevisionField(_KintoneRecordIntField):
    @classmethod
    def field_type(cls) -> str:
        return "__REVISION__"

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordCreatorField(_KintoneRecordUserField):
    @classmethod
    def field_type(cls) -> str:
        return "CREATOR"

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordCreatedTimeField(_KintoneRecordDatetimeField):
    @classmethod
    def field_type(cls) -> str:
        return "CREATED_TIME"

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordModifierField(_KintoneRecordUserField):
    @classmethod
    def field_type(cls) -> str:
        return "MODIFIER"

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordUpdatedTimeField(_KintoneRecordDatetimeField):
    @classmethod
    def field_type(cls) -> str:
        return "UPDATED_TIME"

    @classmethod
    def updatable(cls) -> bool:
        return False


@dataclass
class KintoneRecordSingleLineTextField(_KintoneRecordStrField):
    @classmethod
    def field_type(cls) -> str:
        return "SINGLE_LINE_TEXT"


@dataclass
class KintoneRecordMultiLineTextField(_KintoneRecordStrField):
    @classmethod
    def field_type(cls) -> str:
        return "MULTI_LINE_TEXT"


@dataclass
class KintoneRecordRichTextField(_KintoneRecordStrField):
    @classmethod
    def field_type(cls) -> str:
        return "RICH_TEXT"

    @property
    def text(self) -> str:
        return html.fromstring(f"<div>{self.value}</div>")


@dataclass
class KintoneRecordNumberField(KintoneRecordField[float | None]):
    @classmethod
    def field_type(cls) -> str:
        return "NUMBER"

    def to_json(self) -> dict:
        return {"value": str(self.value) if self.value is not None else None}

    @classmethod
    def from_json(cls, code: str, value: str | float | None) -> KintoneRecordNumberField:
        return cls(code, float(value) if value is not None and value != "" else None)


@dataclass
class KintoneRecordCalcField(_KintoneRecordStrField):
    # TODO: 形式によって使い分ける？
    @classmethod
    def field_type(cls) -> str:
        return "CALC"


@dataclass
class KintoneRecordCheckBoxField(_KintoneRecordSetField):
    @classmethod
    def field_type(cls) -> str:
        return "CHECK_BOX"


@dataclass
class KintoneRecordRadioButtonField(_KintoneRecordOptionalStrField):
    @classmethod
    def field_type(cls) -> str:
        return "RADIO_BUTTON"


@dataclass
class KintoneRecordMultiSelectField(_KintoneRecordSetField):
    @classmethod
    def field_type(cls) -> str:
        return "MULTI_SELECT"


@dataclass
class KintoneRecordDropDownField(_KintoneRecordOptionalStrField):
    @classmethod
    def field_type(cls) -> str:
        return "DROP_DOWN"


@dataclass
class KintoneRecordUserSelectField(_KintoneRecordCodeSelectField):
    @classmethod
    def field_type(cls) -> str:
        return "USER_SELECT"


@dataclass
class KintoneRecordOrgSelectField(_KintoneRecordCodeSelectField):
    @classmethod
    def field_type(cls) -> str:
        return "ORGANIZATION_SELECT"


@dataclass
class KintoneRecordGroupSelectField(_KintoneRecordCodeSelectField):
    @classmethod
    def field_type(cls) -> str:
        return "GROUP_SELECT"


@dataclass
class KintoneRecordDateField(KintoneRecordField[date | None]):
    @classmethod
    def field_type(cls) -> str:
        return "DATE"

    def to_json(self) -> dict:
        if not self.value:
            return {"value": None}
        return {"value": date_to_kintone_str(self.value)}

    @classmethod
    def from_json(cls, code: str, value: Any) -> KintoneRecordDateField:
        if not value:
            return cls(code, None)
        return cls(code, str_to_date(value))


@dataclass
class KintoneRecordTimeField(KintoneRecordField[time | None]):
    @classmethod
    def field_type(cls) -> str:
        return "TIME"

    def to_json(self) -> dict:
        if not self.value:
            return {"value": None}
        return {"value": time_to_kintone_str(self.value)}

    @classmethod
    def from_json(cls, code: str, value: Any) -> KintoneRecordTimeField:
        if not value:
            return cls(code, None)
        return cls(code, str_to_time(value))


@dataclass
class KintoneRecordDateTimeField(KintoneRecordField[datetime | None]):
    def to_json(self) -> dict:
        if not self.value:
            return {"value": None}
        v: datetime = (self.value - timedelta(hours=9)).replace(tzinfo=timezone.utc)
        return {"value": datetime_to_kintone_str(v)}

    @classmethod
    def from_json(cls, code: str, value: str | None) -> KintoneRecordDateTimeField:
        if not value:
            return cls(code, None)
        return cls(code, kintone_str_to_datetime(value))

    @classmethod
    def field_type(cls) -> str:
        return "DATETIME"


@dataclass
class KintoneRecordLinkField(_KintoneRecordStrField):
    @classmethod
    def field_type(cls) -> str:
        return "LINK"


@dataclass
class KintoneRecordFile:
    file_name: str
    content_type: str
    file_key: str | None = None
    file_size: int | None = None


@dataclass
class KintoneRecordFileField(KintoneRecordField[list[KintoneRecordFile]]):
    @classmethod
    def field_type(cls) -> str:
        return "FILE"

    def to_json(self) -> dict:
        return {"value": [{"fileKey": file.file_key} for file in self.value]}

    @classmethod
    def from_json(cls, code: str, value: Any) -> KintoneRecordFileField:
        return cls(
            code,
            [
                KintoneRecordFile(
                    file["name"],
                    file["contentType"],
                    file["fileKey"],
                    int(file["size"])
                ) for file in value
            ])


# # TODO: 参照先によって使い分ける？
# @dataclass
# class KintoneRecordLookupField(_KintoneRecordStrField):
#     @classmethod
#     def field_type(cls) -> str:
#         return "LOOKUP"


@dataclass
class KIntoneRecordSubtableRow:
    id: int | None = None
    fields: dict[str, KintoneRecordField] = field(default_factory=dict)

    def set_field(self, field_: KintoneRecordField) -> None:
        self.fields[field_.code] = field_

    def get_field(self, code: str) -> KintoneRecordField:
        return self.fields[code]


@dataclass
class KintoneRecordSubtableField(KintoneRecordField[list[KIntoneRecordSubtableRow]]):
    @classmethod
    def field_type(cls) -> str:
        return "SUBTABLE"

    def to_json(self) -> dict:
        values: list[dict] = []
        for row in self.value:
            value_json: dict = {
                "value": {
                    field_.code: field_.to_json() for field_ in row.fields.values()
                }
            }
            if row.id is not None:
                value_json["id"] = str(row.id)
            values.append(value_json)
        return {"value": values}

    def add(self, fields: list[KintoneRecordField]) -> None:
        self.value.append(KIntoneRecordSubtableRow(None, {
            field_.code: field_ for field_ in fields
        }))

    def remove(self, row_id: int) -> None:
        self.value = [row for row in self.value if row.id != row_id]

    def get_by_row_id(self, row_id: int) -> KIntoneRecordSubtableRow:
        for row in self.value:
            if row.id == row_id:
                return row
        raise ValueError(f"Row not found: {row_id}")

    def get_by_index(self, index: int) -> KIntoneRecordSubtableRow:
        if index < 0 or index >= len(self.value):
            raise ValueError(f"Index out of range: {index}")
        return self.value[index]

    @classmethod
    def from_json(cls, code: str, value: list[tuple[int, list[KintoneRecordField]]]) -> KintoneRecordSubtableField:
        return cls(code, [
            KIntoneRecordSubtableRow(
                row_id,
                {field_.code: field_ for field_ in fields}
            ) for row_id, fields in value
        ])


class KintoneRecordCategoryField(_KintoneRecordSetField):
    @classmethod
    def field_type(cls) -> str:
        return "CATEGORY"


class KintoneRecordStatusField(_KintoneRecordStrField):
    @classmethod
    def field_type(cls) -> str:
        return "STATUS"


class KintoneRecordAssigneeField(_KintoneRecordCodeSelectField):
    @classmethod
    def field_type(cls) -> str:
        return "STATUS_ASSIGNEE"


_FieldType = TypeVar("_FieldType", bound=KintoneRecordField)


# TODO: @recordclass的なのが作れると良いね
@dataclass
class KintoneRecord:
    app_id: int
    fields: dict[str, KintoneRecordField] = field(default_factory=dict)
    id: int | None = None

    def set_field(self, field_: KintoneRecordField) -> None:
        self.fields[field_.code] = field_

    def remove_field(self, code: str) -> None:
        self.fields.pop(code)

    def get_field(self, code: str, field_type: Type[_FieldType]) -> _FieldType:
        field_: KintoneRecordField = self.fields[code]
        if not isinstance(field_, field_type):
            raise ValueError(f"Field type mismatch: {field_}")
        return field_

    def _get_by_field_type(self, class_: Type[_FieldType]) -> _FieldType:
        for field_ in self.fields.values():
            if field_.field_type() == class_.field_type():
                if not isinstance(field_, class_):
                    raise ValueError(f"Field type mismatch: {field_}")
                return field_
        raise ValueError(f"Field not found: {class_}")

    @property
    def revision(self) -> int:
        return self._get_by_field_type(KintoneRecordRevisionField).value

    @property
    def creator_code(self) -> str:
        return self._get_by_field_type(KintoneRecordCreatorField).value

    @property
    def created_at(self) -> datetime:
        return self._get_by_field_type(KintoneRecordCreatedTimeField).value

    @property
    def modifier_code(self) -> str:
        return self._get_by_field_type(KintoneRecordModifierField).value

    @property
    def updated_at(self) -> datetime:
        return self._get_by_field_type(KintoneRecordUpdatedTimeField).value

    @property
    def categories(self) -> set[str]:
        return self._get_by_field_type(KintoneRecordCategoryField).value

    @property
    def status(self) -> str:
        return self._get_by_field_type(KintoneRecordStatusField).value

    @property
    def assignee_codes(self) -> set[str]:
        return self._get_by_field_type(KintoneRecordAssigneeField).value

    @property
    def field_count(self) -> int:
        return len(self.fields)

    @property
    def field_codes(self) -> set[str]:
        return set(self.fields.keys())
