from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import TypeVar, Type, Any
from zoneinfo import ZoneInfo

from .dto import _KintoneQueryDateFunction, _KintoneQueryFunction, _KintoneQueryUserFunction
from ..dto import KintoneRecordCodeField, KintoneRecordIDField, KintoneRecordCreatorField, \
    KintoneRecordCreatedTimeField, KintoneRecordModifierField, KintoneRecordUpdatedTimeField, \
    KintoneRecordSingleLineTextField, KintoneRecordLinkField, KintoneRecordNumberField, KintoneRecordCalcField, \
    KintoneRecordMultiLineTextField, KintoneRecordRichTextField, KintoneRecordCheckBoxField, \
    KintoneRecordRadioButtonField, KintoneRecordDropDownField, KintoneRecordMultiSelectField, KintoneRecordFileField, \
    KintoneRecordDateField, KintoneRecordTimeField, KintoneRecordDateTimeField, KintoneRecordUserSelectField, \
    KintoneRecordOrgSelectField, KintoneRecordGroupSelectField, KintoneRecordStatusField, KintoneRecordField
from ....util import datetime_to_kintone_str, time_to_kintone_str, date_to_kintone_str

_DEFAULT_GET_RECORD_LIMIT: int = 500

# https://cybozu.dev/ja/kintone/docs/overview/query/#option

_EquableFieldType = TypeVar(
    "_EquableFieldType",
    KintoneRecordCodeField,
    KintoneRecordIDField,
    KintoneRecordCreatedTimeField,
    KintoneRecordUpdatedTimeField,
    KintoneRecordSingleLineTextField,
    KintoneRecordLinkField,
    KintoneRecordNumberField,
    KintoneRecordCalcField,
    KintoneRecordDateField,
    KintoneRecordTimeField,
    KintoneRecordDateTimeField,
    KintoneRecordStatusField
)
_ComparableFieldType = TypeVar(
    "_ComparableFieldType",
    KintoneRecordCodeField,
    KintoneRecordIDField,
    KintoneRecordCreatedTimeField,
    KintoneRecordUpdatedTimeField,
    KintoneRecordNumberField,
    KintoneRecordCalcField,
    KintoneRecordDateField,
    KintoneRecordTimeField,
    KintoneRecordDateTimeField
)
_ContainableFieldType = TypeVar(
    "_ContainableFieldType",
    KintoneRecordCodeField,
    KintoneRecordIDField,
    KintoneRecordCreatorField,
    KintoneRecordModifierField,
    KintoneRecordSingleLineTextField,
    KintoneRecordLinkField,
    KintoneRecordNumberField,
    KintoneRecordCalcField,
    KintoneRecordUserSelectField,
    KintoneRecordOrgSelectField,
    KintoneRecordGroupSelectField,
    KintoneRecordCheckBoxField,
    KintoneRecordRadioButtonField,
    KintoneRecordDropDownField,
    KintoneRecordMultiSelectField,
    KintoneRecordStatusField
)
_LikeableFieldType = TypeVar(
    "_LikeableFieldType",
    KintoneRecordSingleLineTextField,
    KintoneRecordLinkField,
    KintoneRecordMultiLineTextField,
    KintoneRecordRichTextField,
    KintoneRecordFileField
)


def _escape(value: Any, field_type: Type[KintoneRecordField]) -> str:
    if isinstance(value, _KintoneQueryFunction):
        if field_type not in value.field_types():
            raise ValueError(f"unsupported field type: {field_type}")
        return str(value)
    elif isinstance(value, str):
        if '"' in str(value):
            value = value.replace('"', '\"')
        if "\\" in str(value):
            value = value.replace("\\", "\\\\")
        return f'"{value}"'
    elif isinstance(value, datetime):
        return f'"{datetime_to_kintone_str(value.replace(tzinfo=ZoneInfo("Asia/Tokyo")))}"'
    elif isinstance(value, date):
        return f'"{date_to_kintone_str(value)}"'
    elif isinstance(value, time):
        return f'"{time_to_kintone_str(value)}"'
    elif isinstance(value, set):
        return "(" + ", ".join([_escape(v, field_type) for v in sorted(value)]) + ")"
    elif isinstance(value, int) or isinstance(value, float):
        return str(value)
    elif value is None:
        return '""'
    raise NotImplementedError(f"unsupported value type: {type(value)}, field_type: {field_type}")


@dataclass
class _KintonQueryOption:
    fields: set[str] = field(default_factory=set)
    order_by_list: list[tuple[str, bool]] = field(default_factory=list)
    offset: int = 0
    limit: int = _DEFAULT_GET_RECORD_LIMIT


class KintoneQueryBuilder:
    def __init__(self):
        self._conditions: list[str | _KintoneQueryBuilderChild] = []
        self._option: _KintonQueryOption = _KintonQueryOption()

    def _build(self) -> str:
        conditions: list[str] = []
        for c in self._conditions:
            if isinstance(c, _KintoneQueryBuilderChild):
                # noinspection PyProtectedMember
                q: str = c._build()
                # noinspection PyProtectedMember
                symbol: str = "and" if c._is_and else "or"
            else:
                q = str(c)
                symbol = "and"
            if conditions:
                if conditions[-1] in ["(", "and", "or"]:
                    if not q:
                        conditions[-1] = symbol
                else:
                    conditions.append(symbol)
            if not q:
                continue
            conditions.append(q)
        return " ".join(conditions)

    def build(self, is_cursor: bool = False) -> str:
        query: str = self._build()
        if query.count("(") == 1 and query.count(")") == 1 and query.startswith("(") and query.endswith(")"):
            query = query[1:-1]
        if self._option.order_by_list:
            query += " order by " + ", ".join([f"{code} {'desc' if desc else 'asc'}" for code, desc in self._option.order_by_list])
        if is_cursor:
            return query
        query += f" limit {self._option.limit}"
        query += f" offset {self._option.offset}"
        return query.strip()

    def equal(self, code: str, value: str | int | float | datetime | date | _KintoneQueryDateFunction | None, field_type: Type[_EquableFieldType], is_not: bool = False) -> KintoneQueryBuilder:
        symbol: str = "!=" if is_not else "="
        self._conditions.append(f"{code} {symbol} {_escape(value, field_type)}")
        return self

    def _compare(self, code: str, value: str | int | float | datetime | date | _KintoneQueryDateFunction, symbol: str, field_type, equable: bool):
        if equable:
            symbol += "="
        self._conditions.append(f"{code} {symbol} {_escape(value, field_type)}")
        return self

    def greater_than(self, code: str, value: int | float | datetime | date | _KintoneQueryDateFunction, field_type: Type[_ComparableFieldType], equable: bool = False) -> KintoneQueryBuilder:
        self._compare(code, value, ">", field_type, equable)
        return self

    def less_than(self, code: str, value: int | float | datetime | date | _KintoneQueryDateFunction, field_type: Type[_ComparableFieldType], equable: bool = False) -> KintoneQueryBuilder:
        self._compare(code, value, "<", field_type, equable)
        return self

    def contain(self, code: str, value: set[str | _KintoneQueryUserFunction], field_type: Type[_ContainableFieldType], is_not: bool = False) -> KintoneQueryBuilder:
        symbol: str = "not in" if is_not else "in"
        self._conditions.append(f"{code} {symbol} {_escape(value, field_type)}")
        return self

    def like(self, code: str, value: str, field_type: Type[_LikeableFieldType], is_not: bool = False) -> KintoneQueryBuilder:
        symbol: str = "not like" if is_not else "like"
        self._conditions.append(f"{code} {symbol} {_escape(value, field_type)}")
        return self

    def open_(self) -> KintoneQueryBuilder:
        child: _KintoneQueryBuilderChild = _KintoneQueryBuilderChild(parent=self, option=self._option, is_and=True)
        self._conditions.append(child)
        return child

    def close_(self) -> KintoneQueryBuilder:
        return self

    def or_(self) -> KintoneQueryBuilder:
        child: _KintoneQueryBuilderChild = _KintoneQueryBuilderChild(parent=self, option=self._option, is_and=False)
        self._conditions.append(child)
        return child

    def order_by(self, code: str, desc: bool) -> KintoneQueryBuilder:
        self._option.order_by_list.append((code, desc))
        return self

    def offset(self, offset: int) -> KintoneQueryBuilder:
        if offset < 0:
            raise ValueError(f"offset must be non-negative: {offset}")
        elif offset > 10000:
            raise ValueError(f"offset must be less than 10000: {offset}")
        self._option.offset = offset
        return self

    def limit(self, limit: int) -> KintoneQueryBuilder:
        if limit <= 0:
            raise ValueError(f"limit must be positive: {limit}")
        elif limit > 500:
            raise ValueError(f"limit must be less than 500: {limit}")
        self._option.limit = limit
        return self

    def field(self, field_: str) -> KintoneQueryBuilder:
        self._option.fields.add(field_)
        return self

    def fields(self, fields: set[str]) -> KintoneQueryBuilder:
        self._option.fields.update(fields)
        return self

    @property
    def _limit(self) -> int:
        return self._option.limit

    @property
    def _fields(self) -> set[str]:
        return self._option.fields


class _KintoneQueryBuilderChild(KintoneQueryBuilder):
    def __init__(self, parent: KintoneQueryBuilder, option: _KintonQueryOption, is_and: bool = False):
        super().__init__()
        self._parent = parent
        self._option = option
        self._is_and = is_and

    def _build(self) -> str:
        query: str = super()._build()
        if len(self._conditions) > 1:
            query = f"({query})"
        return query

    def build(self, is_cursor: bool = False) -> str:
        return self._parent.build(is_cursor)

    def close_(self) -> KintoneQueryBuilder:
        return self._parent
